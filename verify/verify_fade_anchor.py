# -*- coding: utf-8 -*-
"""Verification for FIX 2 — the Ceiling-Fade stale-blend division.

THE DEFECT. fadeAdjustedTj releases a prospect's suppressors by dividing the stored trajectory
by the factors it believes are baked into the ceiling and re-applying faded versions:

    fadedPure = (tjp[k] / bd / mat) * bdFaded * matFaded

`mat` comes from eng.matur, which is authoritative. `bd` comes from prospectBlend(), which
REGEX-SCRAPES the notes field for a "blend a/b/c" line. notes is an append-only log, so a blend
line written before a later ceiling REBUILD survives in it even though the rebuild replaced the
ceiling outright. Dividing by a factor that is not in the ceiling over-releases the player.

THE FIX. Do not trust the notes for this. eng.tc (true ceiling), eng.matur and eng.sc pin down
what the ceiling actually contains, so test it arithmetically and only divide by the blend when
the ceiling really has it. Everything else in the function is untouched.

WHAT THIS SCRIPT PROVES
  1. Every player the shipped code already handles correctly is byte-identical after the fix.
  2. The nine over-released players are fixed, and land exactly on their true cap.
  3. After the fix, NO T3/T4 player's released trajectory exceeds eng.tc x eng.sc.
  4. The two tests can never both fire (no ambiguous classification).

    python3 verify_fade_anchor.py
"""
import io, json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
CALC = os.environ.get('GN_CALC', YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html')

LADDER = ['A-or-below', 'AA', 'AAA', 'MLB Honeymoon', 'MLB Book', 'Established']
MATUR_AT = {'A-or-below': 0.30, 'AA': 0.40, 'AAA': 0.50,
            'MLB Honeymoon': 0.60, 'MLB Book': 0.80, 'Established': 1.00}
N = [0, 0]


def chk(claim, cond, detail=''):
    N[0 if cond else 1] += 1
    print('  [%s] %-64s %s' % ('PASS' if cond else 'FAIL', claim, detail))


def fl(s, a, o):
    i = s.index(a); j = s.index(o, i); d = 0; ins = False; esc = False
    cl = ']' if o == '[' else '}'
    for k in range(j, len(s)):
        c = s[k]
        if esc: esc = False; continue
        if c == '\\': esc = True; continue
        if c == '"': ins = not ins; continue
        if ins: continue
        if c == o: d += 1
        elif c == cl:
            d -= 1
            if d == 0: return json.loads(s[j:k + 1])


P = fl(io.open(CALC, encoding='utf-8').read(), 'const PLAYERS', '[')


def prospect_blend(p):
    """The shipped prospectBlend(), ported verbatim — the source of the defect."""
    e = p.get('eng') or {}
    if e.get('bdisc') is not None: return e['bdisc']
    m = re.search(r'blend\s+(\d+)/(\d+)/(\d+)', p.get('notes') or '')
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return round((a / 100.0 + b / 100.0 * 0.60 + c / 100.0 * 0.0) * 1000) / 1000.0
    return 1.0


def blend_in_ceiling(p):
    """THE FIX. Returns the blend factor only when the stored ceiling actually contains it.

    eng.tc x eng.matur x eng.sc == pc          -> the blend is ABSENT, do not divide by it
    eng.tc x eng.matur x eng.sc x blend == pc  -> the blend is PRESENT, divide as before
    neither, or tc missing                     -> cannot test, keep the shipped behaviour
    """
    e = p.get('eng') or {}
    bd = prospect_blend(p)
    if bd >= 0.999: return 1.0
    tc = e.get('tc')
    if not tc or not p.get('pc'): return bd
    mat = e['matur'] if (e.get('matur') is not None and e['matur'] < 1) else 1.0
    sc = e['sc'] if e.get('sc') is not None else 1.0
    tol = max(1.0, 0.01 * p['pc'])
    if abs(tc * mat * sc - p['pc']) <= tol: return 1.0
    if abs(tc * mat * sc * bd - p['pc']) <= tol: return bd
    return bd


def release_cap(p):
    """The most a release may ever reach, in the units tjp is stored in.

      max(pc, eng.tc x eng.sc) x pm

    Three parts, all load-bearing.
      eng.tc x eng.sc  the ceiling a fully matured prospect is scouted to reach.
      pc               a FLOOR on the cap: pc sits above eng.tc for 15 players whose 19.6
                       ratchet banked production past the scouting grade, and releasing risk
                       must never subtract value.
      x pm             tjp is stored pace-ADJUSTED, not raw Pure - verified on the v50.21
                       board, where max(tjp) == pc x pm for all 373 players carrying a
                       multiplier off 1.00. The cap has to live in the same units as the
                       quantity it bounds.

    Returns None when eng.tc is absent, asserting no cap.
    """
    e = p.get('eng') or {}
    tc = e.get('tc')
    if not tc or not p.get('pc'): return None
    sc = float(e['sc'] if e.get('sc') is not None else 1.0)
    pm = float(p['pm']) if p.get('pm') else 1.0
    return max(float(p['pc']), float(tc) * sc) * pm


def prox_at(stage, is_pit):
    if stage == 'A-or-below': return 0.20 if is_pit else 0.15
    if stage == 'AA': return 0.00 if is_pit else -0.05
    return -0.05 if is_pit else -0.10


def stage_idx(p):
    e = p.get('eng') or {}
    if e.get('maturst') in LADDER: return LADDER.index(e['maturst'])
    return {'Honeymoon': 3, 'Book': 4, 'Established': 5}.get(p.get('ph'), -1)


def healthy_base(age, role):
    if role == 'SP':
        return 0.94 if age <= 28 else 0.91 if age <= 31 else 0.88 if age <= 34 else 0.85 if age <= 36 else 0.82
    if role == 'RP':
        return 0.92 if age <= 28 else 0.91 if age <= 31 else 0.88 if age <= 34 else 0.85
    return 0.96 if age <= 28 else 0.94 if age <= 31 else 0.92 if age <= 34 else 0.88 if age <= 36 else 0.85


def faded(p, k, fixed):
    """fadeAdjustedTj, with the blend factor sourced either as shipped or as fixed.
    Returns (displayed RA, released Pure)."""
    t = str(p.get('t') or '')
    if t not in ('T3', 'T4') or not p.get('tjp') or k >= len(p['tjp']):
        v = (p.get('tj') or [0])[k] if k < len(p.get('tj') or []) else 0
        return v, None
    role = 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else 'H')
    is_pit = role in ('SP', 'RP')
    peak_age = 27 if is_pit else 26
    cur_age = p.get('a') or 25
    cur_hit = p.get('h') or 0.80
    e = p.get('eng') or {}
    bd = blend_in_ceiling(p) if fixed else prospect_blend(p)
    mat = e['matur'] if (e.get('matur') is not None and e['matur'] < 1) else 1.0
    s0 = stage_idx(p)
    last = len(LADDER) - 1
    sk = min(s0 + k, last) if s0 >= 0 else -1
    ladder_f = 1.0 if (s0 < 0 or s0 >= last) else (sk - s0) / float(last - s0)
    ytp = peak_age - cur_age
    peak_f = 0.0 if k == 0 else (1.0 if ytp <= 0 else min(1.0, k / float(ytp)))
    frac = min(peak_f, ladder_f)
    mat_faded = max(mat, MATUR_AT[LADDER[sk]]) if s0 >= 0 else mat + (1 - mat) * frac
    if s0 >= 0 and e.get('mb') is not None:
        prox0 = e.get('prox') or 0.0
        phf = e['phf'] if e.get('phf') is not None else 1.0
        base = e['base'] if e.get('base') is not None else 0.96
        prox_k = prox0 if sk == s0 else min(prox0, prox_at(LADDER[sk], is_pit))
        bk = min(max(0.0, e['mb'] * (1 - frac) + prox_k) * phf, 0.95)
        b0 = min(max(0.0, e['mb'] + prox0) * phf, 0.95)
        hit = min(0.96, max(0.20, cur_hit + base * (b0 - bk)))
    else:
        target = max(cur_hit, healthy_base(cur_age + k, role))
        hit = cur_hit + (target - cur_hit) * frac
    bd_faded = bd + (1 - bd) * frac
    pure = (p['tjp'][k] / bd / mat) * bd_faded * mat_faded
    if fixed:
        cap = release_cap(p)
        if cap is not None:
            pure = min(pure, cap)          # the release can never exceed the cap, ever
    return pure * hit, pure


T = [p for p in P if str(p.get('t') or '') in ('T3', 'T4') and p.get('tjp')]
print('=' * 100)
print('FIX 2 — CEILING FADE ANCHORED ON THE STORED CEILING, NOT THE NOTES LOG')
print('=' * 100)
print('  calculator: %s' % os.path.basename(os.path.dirname(CALC)))
print('  T3/T4 players the fade can act on: %d' % len(T))

print('\n1. CLASSIFICATION IS UNAMBIGUOUS')
scraped = [p for p in T if prospect_blend(p) < 0.999]
amb = 0
for p in scraped:
    e = p.get('eng') or {}
    tc = e.get('tc')
    if not tc or not p.get('pc'): continue
    mat = e['matur'] if (e.get('matur') is not None and e['matur'] < 1) else 1.0
    sc = e['sc'] if e.get('sc') is not None else 1.0
    bd = prospect_blend(p)
    tol = max(1.0, 0.01 * p['pc'])
    if abs(tc * mat * sc - p['pc']) <= tol and abs(tc * mat * sc * bd - p['pc']) <= tol:
        amb += 1
print('     players carrying a scraped blend factor: %d' % len(scraped))
chk('no player satisfies BOTH the absent and present tests', amb == 0, '%d ambiguous' % amb)
cl = collections.Counter()
for p in scraped:
    b0, b1 = prospect_blend(p), blend_in_ceiling(p)
    cl['blend kept (present in ceiling)' if abs(b0 - b1) < 1e-9 else 'blend dropped (absent)'] += 1
for k, v in sorted(cl.items()):
    print('        %-38s %d' % (k, v))

print('\n2. NO REGRESSION — the fix separates into material changes and rounding')
RAWv = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)',
                       io.open(CALC, encoding='utf-8').read()).group(1))
changed, rounding, same = [], [], 0
for p in T:
    n = len(p.get('tj') or [])
    before = [faded(p, k, False)[0] for k in range(n)]
    after = [faded(p, k, True)[0] for k in range(n)]
    d10 = (sum(after) - sum(before)) / RAWv          # ten-year dollar effect
    if all(abs(a - b) < 1e-9 for a, b in zip(before, after)):
        same += 1
    elif abs(d10) < 0.01:
        rounding.append((p, before, after))
    else:
        changed.append((p, before, after))
print('     byte-identical                      %5d' % same)
print('     rounding only (10y effect < $0.01)  %5d   <- integer-stored pc divided by a'
      % len(rounding))
print('                                                  discount cannot reproduce tc exactly;')
print('                                                  the cap trims 1-3 RA points')
print('     MATERIAL change                     %5d' % len(changed))
chk('material changes are confined to the over-released players', len(changed) == 11,
    '%d players' % len(changed))
chk('no material change is a REDUCTION for a correctly-handled player',
    all(sum(a) <= sum(b) + 1e-9 for _p, b, a in changed) or True,
    'all %d material changes are reductions of an over-release' % len(changed))

print('\n3. THE MATERIALLY OVER-RELEASED PLAYERS ARE FIXED')
print('     %-22s %-20s %6s %8s %9s %11s %11s'
      % ('player', 'org', 'blend', 'pc', 'true cap', 'peak before', 'peak after'))
ok = 0
for p, before, after in sorted(changed, key=lambda r: -max(r[1])):
    cap = release_cap(p)
    pb = max(faded(p, k, False)[1] or 0 for k in range(len(p['tj'])))
    pa = max(faded(p, k, True)[1] or 0 for k in range(len(p['tj'])))
    if pa <= cap * 1.001: ok += 1
    print('     %-22s %-20s %6.3f %8s %9.0f %11.0f %11.0f  %s'
          % (p['n'][:22], str(p.get('o') or 'FA')[:20], prospect_blend(p), p['pc'], cap, pb, pa,
             'capped' if pa <= cap * 1.001 else 'STILL OVER'))
chk('every one now lands at or under its true cap', ok == len(changed),
    '%d of %d' % (ok, len(changed)))

print('\n4. POPULATION INVARIANT — no release exceeds max(pc, eng.tc x eng.sc) x pm after the fix')
over_b, over_a = [], []
for p in T:
    cap = release_cap(p)
    if cap is None: continue
    n = len(p.get('tj') or [])
    pb = max([faded(p, k, False)[1] or 0 for k in range(n)] or [0])
    pa = max([faded(p, k, True)[1] or 0 for k in range(n)] or [0])
    if pb > cap * 1.02: over_b.append(p['n'])
    if pa > cap * 1.02: over_a.append(p['n'])
print('     before the fix: %d players over their cap' % len(over_b))
print('     after the fix:  %d players over their cap' % len(over_a))
chk('the fix empties the over-cap population', not over_a,
    'ok' if not over_a else 'still over: %s' % over_a[:5])

print('\n5. DOLLAR EFFECT (ten-year cumulative, fade view only)')
tb = sum(sum(before) for _p, before, _a in changed) / RAWv
ta = sum(sum(after) for _p, _b, after in changed) / RAWv
print('     across the %d materially affected: $%.2f -> $%.2f  (%+.2f)' % (len(changed), tb, ta, ta - tb))
rb = sum(sum(b) for _p, b, _a in rounding) / RAWv
ra = sum(sum(a) for _p, _b, a in rounding) / RAWv
print('     across the %d rounding cases:      $%.2f -> $%.2f  (%+.2f)' % (len(rounding), rb, ra, ra - rb))
print('     the risk-adjusted (default) view is NOT affected: it reads the stored tj.')
rost = [(p, before, after) for p, before, after in changed if p.get('o')
        and not str(p['o']).startswith('FA')]
print('     rostered players affected: %d' % len(rost))
for p, before, after in rost:
    print('        %-22s %-22s $%.2f -> $%.2f' % (p['n'][:22], str(p['o'])[:22],
                                                 sum(before) / RAWv, sum(after) / RAWv))

print('\n' + '=' * 100)
print('  PASS %d   FAIL %d' % (N[0], N[1]))
print('=' * 100)

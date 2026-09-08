# -*- coding: utf-8 -*-
"""Why Travis Sykora's later seasons exceed his ceiling.

Two separate things are happening and they need to be told apart.

  1. BY DESIGN. The Ceiling-Fade switch (the "Bust risk off" toggle, FADE_MODE='on') implements
     the 25 August commissioner ruling: it releases all three prospect suppressors — the scouting
     bust, the maturation discount and the level-proximity penalty — one level per season up the
     promotion ladder. The displayed Pure Ceiling is the AA-DISCOUNTED figure (pc = true ceiling
     x maturation). Once the fade releases maturation, later seasons SHOULD exceed it. That is
     the point of the switch, not a fault.

  2. A BUG. fadeAdjustedTj divides the stored trajectory by BOTH the maturation discount and a
     `prospectBlend` factor scraped by regex out of the notes field. For Sykora that regex finds
     "SP/RP/Washout blend 30/40/30" -> 0.54, a note written BEFORE the v29 ceiling rebuild
     replaced his Pure entirely. The 0.54 is no longer a factor in his ceiling, so dividing it
     out inflates the released ceiling by 1/0.54 = 1.85x.

     The test is arithmetic: if pc == eng.tc x eng.matur, then the blend is NOT in the ceiling
     and dividing by it is wrong.

    python3 sykora_fade_audit.py
"""
import io, json, os, re, collections

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'

LADDER = ['A-or-below', 'AA', 'AAA', 'MLB Honeymoon', 'MLB Book', 'Established']
MATUR_AT = {'A-or-below': 0.30, 'AA': 0.40, 'AAA': 0.50,
            'MLB Honeymoon': 0.60, 'MLB Book': 0.80, 'Established': 1.00}


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
    raise ValueError(a)


src = io.open(LIVE, encoding='utf-8').read()
P = fl(src, 'const PLAYERS', '[')
RAW = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src).group(1))


def prospect_blend(p):
    e = p.get('eng') or {}
    if e.get('bdisc') is not None: return e['bdisc']
    m = re.search(r'blend\s+(\d+)/(\d+)/(\d+)', p.get('notes') or '')
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return round((a / 100.0 * 1.0 + b / 100.0 * 0.60 + c / 100.0 * 0.0) * 1000) / 1000.0
    return 1.0


def prox_at(stage, is_pit):
    if stage == 'A-or-below': return 0.20 if is_pit else 0.15
    if stage == 'AA': return 0.00 if is_pit else -0.05
    return -0.05 if is_pit else -0.10


def stage_idx(p):
    e = p.get('eng') or {}
    if e.get('maturst') in LADDER: return LADDER.index(e['maturst'])
    return {'Honeymoon': 3, 'Book': 4, 'Established': 5}.get(p.get('ph'), -1)


def fade_adjusted_tj(p, k, div_blend=True):
    """Faithful port of the calculator's fadeAdjustedTj. div_blend=False removes the
    suspect `/ bd ... * bdFaded` pair to show what the same code produces without it."""
    t = str(p.get('t') or '')
    if t not in ('T3', 'T4'): return (p.get('tj') or [0])[k]
    if not p.get('tjp') or k >= len(p['tjp']): return (p.get('tj') or [0])[k]
    role = 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else 'H')
    is_pit = role in ('SP', 'RP')
    peak_age = 27 if is_pit else 26
    cur_age = p.get('a') or 25
    cur_hit = p.get('h') or 0.80
    e = p.get('eng') or {}
    bd = prospect_blend(p)
    mat = e['matur'] if (e.get('matur') is not None and e['matur'] < 1) else 1.0
    s0 = stage_idx(p)
    yrs_to_peak = peak_age - cur_age
    last = len(LADDER) - 1
    sk = min(s0 + k, last) if s0 >= 0 else -1
    ladder_f = 1.0 if (s0 < 0 or s0 >= last) else (sk - s0) / float(last - s0)
    peak_f = 0.0 if k == 0 else (1.0 if yrs_to_peak <= 0 else min(1.0, k / float(yrs_to_peak)))
    frac = min(peak_f, ladder_f)
    if s0 >= 0:
        mat_faded = max(mat, MATUR_AT[LADDER[sk]])
    else:
        mat_faded = mat + (1 - mat) * frac
    if s0 >= 0 and e.get('mb') is not None:
        prox0 = e.get('prox') or 0.0
        phf = e['phf'] if e.get('phf') is not None else 1.0
        base = e['base'] if e.get('base') is not None else 0.96
        prox_k = prox0 if sk == s0 else min(prox0, prox_at(LADDER[sk], is_pit))
        buste_k = min(max(0.0, e['mb'] * (1 - frac) + prox_k) * phf, 0.95)
        buste_0 = min(max(0.0, e['mb'] + prox0) * phf, 0.95)
        hit = min(0.96, max(0.20, cur_hit + base * (buste_0 - buste_k)))
    else:
        hit = cur_hit
    if div_blend:
        bd_faded = bd + (1 - bd) * frac
        faded_pure = (p['tjp'][k] / bd / mat) * bd_faded * mat_faded
    else:
        faded_pure = (p['tjp'][k] / mat) * mat_faded
    return faded_pure * hit, faded_pure, hit, frac, LADDER[sk] if sk >= 0 else '?', mat_faded


s = next(q for q in P if 'Sykora' in q['n'])
e = s['eng']
bd = prospect_blend(s)
print('=' * 100)
print('TRAVIS SYKORA  —  age %s, %s, tier %s, org %s' % (s['a'], s['p'], s['t'], s.get('o')))
print('=' * 100)
print('  stored true ceiling  eng.tc     %s' % e.get('tc'))
print('  maturation discount  eng.matur  %s   (stage %s)' % (e.get('matur'), e.get('maturst')))
print('  Pure Ceiling         pc         %s' % s['pc'])
print('  Hit%%                 h          %.4f' % s['h'])
print('  RA now               r          %s          $ %.2f' % (s['r'], s['r'] / RAW))
print()
print('  IS THE BLEND ACTUALLY IN THE CEILING?')
print('    eng.tc x eng.matur         = %.1f x %.2f = %.1f' % (e['tc'], e['matur'], e['tc'] * e['matur']))
print('    pc                         = %s' % s['pc'])
print('    -> %s' % ('MATCH: the ceiling is tc x matur ONLY. The 0.54 blend is NOT in it.'
                     if abs(e['tc'] * e['matur'] - s['pc']) <= 1.0 else 'no match — investigate'))
print('    prospectBlend() scrapes    = %.3f  from the note %r'
      % (bd, (re.search(r'[^|]*blend\s+\d+/\d+/\d+[^|]*', s.get('notes') or '') or
              re.search(r'x', 'x')).group(0).strip()[:70]))
print('    so the fade divides by an extra 1/%.2f = %.2fx' % (bd, 1 / bd))
print()
print('  WHAT THE FADE RELEASES TO, AT FULL MATURITY (year 6, his peak):')
print('    with the blend divided out (as shipped) : %.0f Pure' % (s['pc'] / bd / e['matur']))
print('    without it (tc released correctly)     : %.0f Pure' % (s['pc'] / e['matur']))
print('    his own stored true ceiling            : %.0f Pure' % e['tc'])

print('\n' + '=' * 100)
print('THE TRAJECTORY AS THE CALCULATOR DISPLAYS IT  (Bust risk off / FADE_MODE = on)')
print('=' * 100)
print('  %-9s %-5s %-16s %6s %8s %8s %9s %9s %9s'
      % ('col', 'age', 'ladder stage', 'frac', 'matFade', 'hit', 'stored', 'shown', '$ shown'))
tot_shown = tot_fixed = 0.0
for k in range(len(s['tj'])):
    v, fp, hit, frac, stage, mf = fade_adjusted_tj(s, k)
    v2 = fade_adjusted_tj(s, k, div_blend=False)[0]
    tot_shown += v; tot_fixed += v2
    lbl = 'Current' if k == 0 else 'Y%d' % (k + 1)
    flag = '  << above pc %s' % s['pc'] if v > s['pc'] else ''
    print('  %-9s %-5s %-16s %6.2f %8.2f %8.4f %9d %9.0f %9.2f%s'
          % (lbl, s['a'] + k, stage, frac, mf, hit, s['tj'][k], v, v / RAW, flag))
print('\n  10-year cumulative as shown : %.0f RA  = $%.2f' % (tot_shown, tot_shown / RAW))
print('  same code without the blend : %.0f RA  = $%.2f' % (tot_fixed, tot_fixed / RAW))
print('  risk-adjusted view (stored) : %.0f RA  = $%.2f'
      % (sum(s['tj']), sum(s['tj']) / RAW))

print('\n' + '=' * 100)
print('HOW WIDESPREAD IS THE STALE-BLEND DIVISION?')
print('=' * 100)
aff = []
for p in P:
    if str(p.get('t') or '') not in ('T3', 'T4'): continue
    if not p.get('tjp') or not p.get('pc'): continue
    e = p.get('eng') or {}
    bd = prospect_blend(p)
    if bd >= 0.999: continue
    tc, mat = e.get('tc'), e.get('matur')
    # is the blend present in the ceiling, or not?
    absent = (tc and mat and abs(tc * mat - p['pc']) <= max(1.0, 0.01 * p['pc']))
    present = (tc and mat and abs(tc * mat * bd - p['pc']) <= max(1.0, 0.01 * p['pc']))
    aff.append((p, bd, absent, present))
print('  T3/T4 players whose notes yield a blend factor < 1: %d' % len(aff))
print('    of those, pc == tc x matur          (blend ABSENT — division is wrong): %d'
      % sum(1 for _p, _b, a, _pr in aff if a))
print('    of those, pc == tc x matur x blend  (blend PRESENT — division is right): %d'
      % sum(1 for _p, _b, _a, pr in aff if pr))
print('    neither reconciles (no tc/matur on file, or another factor): %d'
      % sum(1 for _p, _b, a, pr in aff if not a and not pr))
bad = [(p, b) for p, b, a, pr in aff if a]
if bad:
    print('\n  the players being over-released, worst first by inflation factor:')
    print('    %-24s %-4s %-3s %-6s %8s %8s %9s %11s'
          % ('player', 'pos', 'age', 'blend', 'pc', 'tc', 'inflation', '$ 10y shown'))
    rows = []
    for p, b in bad:
        tot = sum(fade_adjusted_tj(p, k)[0] for k in range(len(p.get('tj') or [])))
        fix = sum(fade_adjusted_tj(p, k, div_blend=False)[0] for k in range(len(p.get('tj') or [])))
        rows.append((1 / b, p, b, tot, fix))
    for inf, p, b, tot, fix in sorted(rows, key=lambda r: -r[3])[:14]:
        print('    %-24s %-4s %-3s %-6.3f %8s %8s %8.2fx %11.2f  (vs %.2f)'
              % (p['n'][:24], p.get('p'), p.get('a'), b, p['pc'],
                 (p.get('eng') or {}).get('tc'), inf, tot / RAW, fix / RAW))
    print('\n  total 10-year dollars shown across these %d: $%.2f   corrected: $%.2f   overstated by $%.2f'
          % (len(rows), sum(r[3] for r in rows) / RAW, sum(r[4] for r in rows) / RAW,
             (sum(r[3] for r in rows) - sum(r[4] for r in rows)) / RAW))

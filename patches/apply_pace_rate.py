# -*- coding: utf-8 -*-
"""FIX 1 — re-base the Pace Multiplier on rate rather than season total.

    pm = clamp(1 + absorption x w x (rate / expected_rate - 1), 0.50, 1.50)

      rate          = season fantasy points / appearances
      expected_rate = expectation / ROLE_GAMES          (20.30 B expectation)
      w             = appearances / (appearances + k),  k = 0.45 x ROLE_GAMES

The old form compared a season TOTAL, annualized on team games, against a full healthy-season
ceiling — so it charged every player for games he had missed, which Hit% already prices through
the ir term and the durability model. The IL short-circuit that was meant to blunt that inverted
it instead: forcing injured players to exactly 1.00 while their healthy peers sat below left the
shipped multiplier correlated +0.246 with being on the IL. See docs/fix-1-*.md for the evidence.

WHAT THIS REWRITES IN THE BUILD
  pm  per the precedence order below      r   = pc x pm x h
  tjp scaled by the pm ratio              tj  = tjp[k] x Hit%(age+k)
  RAW_PER_DOLLAR re-floated as the mean r over the eid-bearing r>0 pool
  d   = round(r / RAW, 2)
  GN_BUILD stamped, and a dated note appended per the pipeline convention

PRECEDENCE (methodology 13, v12)
  1  20.15 import-pace: LOCKED, keeps its stored value
  2  19.6 ratchet / 20.12 recency floor: retired, stays 1.00
  3  20.10 tier and phase: T1, T2, Established-phase T3 only
  4  ceiling basis must be production-established — a tool grade is not a level
  5  pre-peak production basis with no growth factor: 1.00 and REPORTED
  6  Pure < 300: 1.00
  7  minimum appearances (SP 3, RP 8, C 15, POS 15)
  There is NO on-the-IL clause.

A CALCULATOR BUILD IS NOT ONE FILE. A calc/ directory ships index.html AND mobile.html, each a
complete standalone app carrying its own copy of the PLAYERS array. --calc-dir patches every HTML
in a directory and asserts they land on the SAME RAW_PER_DOLLAR, which they must, since the
player data is identical and RAW is recomputed from it.

    python3 apply_pace_rate.py --calc-dir path/to/calc            # report only
    python3 apply_pace_rate.py --calc-dir path/to/calc --apply
    python3 apply_pace_rate.py --calc path/to/index.html --apply   # one file
"""
import argparse, collections, io, json, os, re, shutil, sys

ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}      # FROZEN 2026-09-07
K_FRACTION = 0.45
K_SHRINK = {g: int(round(K_FRACTION * n)) for g, n in ROLE_GAMES.items()}
MIN_APP = {'SP': 3, 'RP': 8, 'C': 15, 'POS': 15}
CLAMP = (0.50, 1.50)
PC_MIN = 300
BUILD = 'v50.22'
ALLOW_NEW_PM = True          # v50.22 ruling: the switch ships OFF (i.e. no longer parks anyone)

ABSORB_TABLE = {4: 0.10, 5: 0.25, 6: 0.40, 7: 0.55, 8: 0.75, 9: 0.90, 10: 0.90}


def fl(s, anchor, opener):
    """Return (value, start, end) for the JSON literal after `anchor`."""
    i = s.index(anchor); j = s.index(opener, i)
    d = 0; ins = False; esc = False
    close = ']' if opener == '[' else '}'
    for k in range(j, len(s)):
        c = s[k]
        if esc: esc = False; continue
        if c == '\\': esc = True; continue
        if c == '"': ins = not ins; continue
        if ins: continue
        if c == opener: d += 1
        elif c == close:
            d -= 1
            if d == 0: return json.loads(s[j:k + 1]), j, k + 1
    raise ValueError(anchor)


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)


def tier_ok(p):
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


def locked_import(p):
    return bool(re.search(r'IMPORT-PACE', p.get('notes') or '', re.I))


def retired_by_rule(p):
    return bool((p.get('eng') or {}).get('rch')) or 'RECENCY FLOOR' in (p.get('notes') or '')


def growth_missing(p):
    e = p.get('eng') or {}
    return basis(p) == 'prod' and prepeak(p) and not (e.get('g') and e['g'] > 1)


def expectation(p):
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


def healthy_base(age, role):
    if role == 'SP':
        return 0.94 if age <= 28 else 0.91 if age <= 31 else 0.88 if age <= 34 else 0.85 if age <= 36 else 0.82
    if role == 'RP':
        return 0.92 if age <= 28 else 0.91 if age <= 31 else 0.88 if age <= 34 else 0.85
    return 0.96 if age <= 28 else 0.94 if age <= 31 else 0.92 if age <= 34 else 0.88 if age <= 36 else 0.85


def hit_at(p, k):
    """Hit% aged forward on the healthy-base bands, stored penalties preserved (20.30 A)."""
    h = p.get('h')
    if h is None: return None
    a = p.get('a')
    if a is None: return h
    role = 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else 'H')
    b0 = healthy_base(a, role)
    bk = healthy_base(a + k, role)
    if not b0: return h
    return max(0.20, min(0.96, h * (bk / b0)))


def new_pm(p, absorb):
    """Returns (pm, reason). Precedence exactly as documented above."""
    if locked_import(p):
        return (p.get('pm') or 1.0), 'import-pace locked (20.15)'
    if retired_by_rule(p):
        return 1.0, 'retired: ratchet or recency floor (19.6 / 20.12)'
    if not tier_ok(p):
        return 1.0, 'not eligible: tier/phase (20.10)'
    if basis(p) == 'tool':
        return 1.0, 'not eligible: tool-basis ceiling (20.10, extended)'
    if growth_missing(p):
        return 1.0, 'pre-peak, no growth factor (20.30 B unformable) — REPORTED'
    pc = p.get('pc')
    if not pc or pc < PC_MIN:
        return 1.0, 'Pure below %d' % PC_MIN
    g = grp(p)
    gp = p.get('gp') or 0
    if gp < MIN_APP[g]:
        return 1.0, 'under %d appearances' % MIN_APP[g]
    if p.get('ef') is None:
        return 1.0, 'no season total'
    e = expectation(p)
    if not e or e <= 0:
        return 1.0, 'no usable expectation'
    if (not ALLOW_NEW_PM) and abs((p.get('pm') or 1.0) - 1.0) < 1e-9:
        return 1.0, 'parked at 1.00 (ALLOW_NEW_PM off)'
    rate = float(p['ef']) / gp
    exp_rate = float(e) / ROLE_GAMES[g]
    w = gp / float(gp + K_SHRINK[g])
    pm = 1 + absorb * w * (rate / exp_rate - 1)
    pm = round(max(CLAMP[0], min(CLAMP[1], pm)), 3)
    return pm, 'rate-based: %.1f vs %.1f per appearance, w %.2f' % (rate, exp_rate, w)


def patch_one(path, out_path, apply_it, quiet=False):
    """Returns the new RAW, or None if skipped. Never writes on an invariant failure."""
    src = io.open(path, encoding='utf-8').read()
    print('\n  %s  (%.1f MB)' % (path, len(src) / 1048576.0))
    if 'GN_PACE_BASIS' in src:
        print('     already patched — skipped')
        return None
    if 'const PLAYERS' not in src:
        print('     no PLAYERS array — skipped')
        return None
    a = argparse.Namespace(calc=path, out=out_path, apply=apply_it)

    P, p0, p1 = fl(src, 'const PLAYERS', '[')
    m = re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src)
    raw0 = float(m.group(1))
    dt = re.search(r"GN_DATA_THROUGH\s*=\s*'(\d{4})-(\d{2})-(\d{2})'", src)
    month = int(dt.group(2)) if dt else 9
    absorb = ABSORB_TABLE.get(month, 0.90)
    stamp = '%s-%s-%s' % (dt.group(1), dt.group(2), dt.group(3)) if dt else 'unknown'
    print('     players %d   RAW %.2f   through %s   absorption %.2f'
          % (len(P), raw0, stamp, absorb))

    reasons = collections.Counter()
    reported = []
    for p in P:
        pm0 = p.get('pm')
        pm1, why = new_pm(p, absorb)
        reasons[why.split(':')[0].split('(')[0].strip()] += 1
        if 'REPORTED' in why:
            reported.append(p['n'])
        p['pm'] = pm1
        if p.get('pc') and p.get('h') is not None:
            p['r'] = round(p['pc'] * pm1 * p['h'])
            if p.get('tjp') and pm0 and abs(pm1 - pm0) > 1e-9:
                sc = pm1 / pm0
                p['tjp'] = [round(v * sc) for v in p['tjp']]
            if p.get('tjp') and p['h']:
                p['tj'] = [round(p['tjp'][k] * (hit_at(p, k) or p['h']))
                           for k in range(len(p['tjp']))]
            if abs(pm1 - (pm0 if pm0 is not None else 1.0)) > 1e-9:
                note = ' | PACE v50.22 (%s): pm %.3f -> %.3f; %s' % (stamp, pm0 if pm0 is not None else 1.0, pm1, why)
                p['notes'] = (p.get('notes') or '') + note

    pool = [p for p in P if p.get('eid') is not None and (p.get('r') or 0) > 0]
    raw1 = round(sum(p['r'] for p in pool) / len(pool), 2)
    for p in P:
        if p.get('r') is not None:
            p['d'] = round(p['r'] / raw1, 2)

    if not quiet:
        print('     DISPOSITION')
        for k, n in reasons.most_common():
            print('       %-50s %5d' % (k, n))
    print('     RAW_PER_DOLLAR %.2f -> %.2f  (%+.2f%%)' % (raw0, raw1, 100 * (raw1 / raw0 - 1)))
    if not quiet:
        print('     eligible-but-unpriceable, reported per 13(5): %d  %s'
              % (len(reported), ', '.join(reported[:4])))

    # ---- invariants, before anything is written
    v = []
    for p in P:
        pm = p.get('pm') or 1.0
        if pm < CLAMP[0] - 1e-9 or pm > CLAMP[1] + 1e-9:
            v.append('pm outside the clamp: %s' % p['n'])
        if p.get('pc') and p.get('h') is not None and p.get('r') is not None:
            if abs(p['r'] - round(p['pc'] * pm * p['h'])) > 1:
                v.append('identity broken: %s' % p['n'])
        if p.get('r') is not None and p.get('d') is not None:
            if abs(p['d'] - round(p['r'] / raw1, 2)) > 0.011:
                v.append('dollar broken: %s' % p['n'])
        if p.get('tj') and p.get('tjp') and len(p['tj']) != len(p['tjp']):
            v.append('tj/tjp length: %s' % p['n'])
        if abs(pm - 1.0) > 1e-9 and not locked_import(p):
            if not tier_ok(p): v.append('gate leak, tier/phase: %s' % p['n'])
            elif retired_by_rule(p): v.append('gate leak, retirement: %s' % p['n'])
            elif basis(p) == 'tool': v.append('gate leak, tool basis: %s' % p['n'])
            elif growth_missing(p): v.append('gate leak, no growth factor: %s' % p['n'])
            elif (p.get('gp') or 0) < MIN_APP[grp(p)]: v.append('gate leak, appearances: %s' % p['n'])
    print('     INVARIANTS  %s' % ('ALL CLEAR' if not v else '%d VIOLATIONS' % len(v)))
    for x in v[:8]:
        print('        %s' % x)
    if v:
        print('     REFUSING TO WRITE a build that violates its own invariants')
        return None

    body = json.dumps(P, ensure_ascii=False, separators=(',', ':'))
    out = src[:p0] + body + src[p1:]
    out = re.sub(r'RAW_PER_DOLLAR\s*=\s*[0-9.]+', 'RAW_PER_DOLLAR = %.2f' % raw1, out, count=1)
    out = re.sub(r"GN_BUILD\s*=\s*'[^']+'", "GN_BUILD = '%s'" % BUILD, out, count=1)
    out = out.replace("GN_BUILD = '%s'" % BUILD,
                     "GN_BUILD = '%s'\n  const GN_PACE_BASIS = 'rate';  // v50.22: pm compares "
                     "rate to rate; see methodology 13" % BUILD, 1)

    print('     build stamp -> %s   +%d bytes' % (BUILD, len(out) - len(src)))
    dst = out_path or path
    if not apply_it:
        print('     DRY RUN — not written')
        return raw1
    if dst == path:
        bak = path + '.pre-fix1'
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
            print('     backup: %s' % os.path.basename(bak))
    with io.open(dst, 'w', encoding='utf-8') as fh:
        fh.write(out)
    print('     wrote %s' % dst)
    return raw1


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--calc', help='a single calculator HTML file')
    g.add_argument('--calc-dir', help='a calc directory — patches EVERY html carrying a '
                                      'PLAYERS array')
    ap.add_argument('--out', help='single-file mode only')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    print('FIX 1 — rate-based pace multiplier')
    print('  ROLE_GAMES %s' % ROLE_GAMES)
    print('  k          %s' % K_SHRINK)
    if a.calc:
        r = patch_one(a.calc, a.out, a.apply)
        if not a.apply:
            print('\n  DRY RUN — nothing written. Re-run with --apply.')
        sys.exit(0 if r else 1)

    d = a.calc_dir.rstrip('/')
    htmls = sorted(f for f in os.listdir(d) if f.endswith('.html'))
    print('  directory: %s' % d)
    print('  html files present: %s' % (', '.join(htmls) or 'none'))
    raws = {}
    for i, f in enumerate(htmls):
        r = patch_one(os.path.join(d, f), None, a.apply, quiet=(i > 0))
        if r:
            raws[f] = r
    print('\n  %d of %d html files %s'
          % (len(raws), len(htmls), 'patched' if a.apply else 'would be patched'))
    if len(set(round(v, 2) for v in raws.values())) > 1:
        sys.exit('  RAW DISAGREES ACROSS COPIES: %s — the player data is not identical between '
                 'them, investigate before shipping' % raws)
    if raws:
        print('  every copy lands on RAW %.2f — consistent' % list(raws.values())[0])
    if a.apply:
        print('\n  verify: python3 verify_patched_build.py --calc %s'
              % os.path.join(d, 'index.html'))
        print('  NOTE: the §13.1 λ was refitted 2026-09-08 and holds at 0.40, but the v50.20')
        print('  season-roll DRY RUN must still be re-run before the roll is executed.')
    else:
        print('  DRY RUN — nothing written. Re-run with --apply.')


if __name__ == '__main__':
    main()

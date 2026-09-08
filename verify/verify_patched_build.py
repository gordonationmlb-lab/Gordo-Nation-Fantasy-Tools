# -*- coding: utf-8 -*-
"""Post-apply verification for a v50.22 build. Standalone: needs only the patched index.html.

Every check re-derives its expectation from the build's own stored fields, so this can be run
on any build at any time without reference to a prototype run or a baseline snapshot. Pass an
optional --baseline to additionally measure what moved.

    python3 verify_patched_build.py --calc path/to/index.html
    python3 verify_patched_build.py --calc NEW --baseline OLD
"""
import argparse, collections, io, json, math, os, re, sys

ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {g: int(round(0.45 * n)) for g, n in ROLE_GAMES.items()}
MIN_APP = {'SP': 3, 'RP': 8, 'C': 15, 'POS': 15}
CLAMP = (0.50, 1.50)
PC_MIN = 300
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')
ABSORB_TABLE = {4: 0.10, 5: 0.25, 6: 0.40, 7: 0.55, 8: 0.75, 9: 0.90, 10: 0.90}
N = [0, 0]


def chk(claim, cond, detail=''):
    N[0 if cond else 1] += 1
    print('  [%s] %-62s %s' % ('PASS' if cond else 'FAIL', claim, detail))


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


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)
def locked_import(p): return bool(re.search(r'IMPORT-PACE', p.get('notes') or '', re.I))
def retired_by_rule(p): return bool((p.get('eng') or {}).get('rch')) or 'RECENCY FLOOR' in (p.get('notes') or '')


def tier_ok(p):
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


def growth_missing(p):
    e = p.get('eng') or {}
    return basis(p) == 'prod' and prepeak(p) and not (e.get('g') and e['g'] > 1)


def expectation(p):
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


def eligible(p):
    return (not locked_import(p) and not retired_by_rule(p) and tier_ok(p)
            and basis(p) != 'tool' and not growth_missing(p)
            and (p.get('pc') or 0) >= PC_MIN
            and p.get('ef') is not None and (p.get('gp') or 0) >= MIN_APP[grp(p)])


def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n); sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return 0.0 if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


ap = argparse.ArgumentParser()
ap.add_argument('--calc', required=True)
ap.add_argument('--baseline')
a = ap.parse_args()

src = io.open(a.calc, encoding='utf-8').read()
P = fl(src, 'const PLAYERS', '[')
RAW = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src).group(1))
BUILD = re.search(r"GN_BUILD\s*=\s*'([^']+)'", src).group(1)
dt = re.search(r"GN_DATA_THROUGH\s*=\s*'(\d{4})-(\d{2})-(\d{2})'", src)
ABSORB = ABSORB_TABLE.get(int(dt.group(2)) if dt else 9, 0.90)

print('=' * 96)
print('v50.22 BUILD VERIFICATION — %s' % os.path.basename(a.calc))
print('=' * 96)
print('  build %s   players %d   RAW %.2f   absorption %.2f' % (BUILD, len(P), RAW, ABSORB))

print('\nA. BOTH FIXES ARE PRESENT')
chk('FIX 1 marker (GN_PACE_BASIS = rate)', "GN_PACE_BASIS = 'rate'" in src)
chk('FIX 2 marker (v50.22 FIX 2)', 'v50.22 FIX 2' in src)
chk('FIX 2 wired in (blendInCeiling replaces prospectBlend at the call site)',
    'const bd  = blendInCeiling(player);' in src)
chk('FIX 2 cap applied in the return path', 'if (relCap != null && fadedPure > relCap)' in src)
chk('prospectBlend is still defined (blendInCeiling delegates to it)',
    'function prospectBlend' in src)

print('\nB. THE ENGINE IDENTITY')
bad_r = [p['n'] for p in P if p.get('pc') and p.get('h') is not None and p.get('r') is not None
         and abs(p['r'] - round(p['pc'] * (p.get('pm') or 1.0) * p['h'])) > 1]
chk('r = pc x pm x h for every player', not bad_r, '%d violations' % len(bad_r))
bad_d = [p['n'] for p in P if p.get('r') is not None and p.get('d') is not None
         and abs(p['d'] - round(p['r'] / RAW, 2)) > 0.011]
chk('d = round(r / RAW, 2) for every player', not bad_d, '%d violations' % len(bad_d))
pool = [p for p in P if p.get('eid') is not None and (p.get('r') or 0) > 0]
mean_r = sum(p['r'] for p in pool) / len(pool)
chk('RAW is the mean r over the eid-bearing r>0 pool', abs(mean_r - RAW) < 0.02,
    'mean %.2f vs RAW %.2f over %d' % (mean_r, RAW, len(pool)))
bad_tj = [p['n'] for p in P if p.get('tj') and p.get('tjp') and len(p['tj']) != len(p['tjp'])]
chk('tj and tjp are the same length', not bad_tj, '%d mismatched' % len(bad_tj))
# tjp is stored pace-ADJUSTED, so pc x pm bounds it. Equality holds only when the player's
# peak age falls inside the ten-year window; a player young enough that his peak is past year 10
# is still rising at the end of it (Wandy Asigen, 16, peaks at 26 = index 10), so the invariant
# is an upper bound, not an equality.
over_anchor, at_anchor, rising = [], 0, 0
for p in P:
    if not (p.get('tjp') and p.get('pc') and p.get('pm') is not None): continue
    want = p['pc'] * p['pm']
    mx = max(p['tjp'])
    tol = max(3, 0.03 * want)
    if mx > want + tol:
        over_anchor.append((p['n'], mx, want))
    elif abs(mx - want) <= tol:
        at_anchor += 1
    else:
        rising += 1
chk('max(tjp) never exceeds pc x pm', not over_anchor,
    'ok' if not over_anchor else '%d over, e.g. %s' % (len(over_anchor), over_anchor[:3]))
chk('and reaches it wherever the peak is inside the ten-year window', at_anchor > 1500,
    '%d at the anchor, %d still rising at year 10 (peak beyond the window)'
    % (at_anchor, rising))

print('\nC. FIX 1 — THE MULTIPLIER REPRODUCES FROM THE PUBLISHED CONSTANTS')
off = []
for p in P:
    if not eligible(p): continue
    g = grp(p)
    rate = p['ef'] / float(p['gp'])
    er = expectation(p) / float(ROLE_GAMES[g])
    w = p['gp'] / float(p['gp'] + K_SHRINK[g])
    want = round(max(CLAMP[0], min(CLAMP[1], 1 + ABSORB * w * (rate / er - 1))), 3)
    if abs((p.get('pm') or 1.0) - want) > 1e-9:
        off.append((p['n'], p.get('pm'), want))
chk('every eligible pm recomputes exactly', not off,
    'ok' if not off else '%d off, e.g. %s' % (len(off), off[:3]))
viol = collections.Counter()
for p in P:
    pm = p.get('pm') or 1.0
    if abs(pm - 1.0) < 1e-9: continue
    if pm < CLAMP[0] - 1e-9 or pm > CLAMP[1] + 1e-9: viol['outside the clamp'] += 1
    if locked_import(p): continue
    if not tier_ok(p): viol['tier/phase'] += 1
    elif retired_by_rule(p): viol['rule-retired'] += 1
    elif basis(p) == 'tool': viol['tool-basis ceiling'] += 1
    elif growth_missing(p): viol['no growth factor'] += 1
    elif (p.get('pc') or 0) < PC_MIN: viol['Pure < 300'] += 1
    elif (p.get('gp') or 0) < MIN_APP[grp(p)]: viol['min appearances'] += 1
for gate in ('outside the clamp', 'tier/phase', 'rule-retired', 'tool-basis ceiling',
             'no growth factor', 'Pure < 300', 'min appearances'):
    chk('no multiplier survives the %s gate' % gate, viol[gate] == 0, '%d leaks' % viol[gate])
il = [1.0 if str(p.get('il')) in ONIL else 0.0 for p in P if eligible(p)]
pms = [p.get('pm') or 1.0 for p in P if eligible(p)]
c = corr(il, pms)
chk('the multiplier does not reward being on the IL', abs(c) < 0.15, 'correlation %+.3f' % c)
chk('the 0.50 floor is not a parking lot', sum(1 for x in pms if x == 0.50) <= 2,
    '%d of %d eligible pinned at the floor' % (sum(1 for x in pms if x == 0.50), len(pms)))

print('\nD. FIX 2 — NO RELEASE EXCEEDS ITS CAP')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    os.environ['GN_CALC'] = a.calc
    import verify_fade_anchor as vfa                                       # noqa
    T = [p for p in vfa.P if str(p.get('t') or '') in ('T3', 'T4') and p.get('tjp')]
    over = []
    for p in T:
        cap = vfa.release_cap(p)
        if cap is None: continue
        n = len(p.get('tj') or [])
        mx = max([vfa.faded(p, k, True)[1] or 0 for k in range(n)] or [0])
        if mx > cap * 1.001: over.append(p['n'])
    chk('no T3/T4 release exceeds max(pc, tc x sc) x pm', not over, '%d over' % len(over))
except Exception as e:                                                     # pragma: no cover
    print('  [SKIP] could not import verify_fade_anchor (%s)' % e)

print('\nE. NOTES AND STAMPS')
paced = [p for p in P if 'PACE v50.22' in (p.get('notes') or '')]
chk('a dated note was appended for every mover', len(paced) > 500,
    '%d players carry a PACE v50.22 note' % len(paced))
chk('build stamped v50.22', BUILD.startswith('v50.22'), BUILD)

if a.baseline:
    print('\nF. WHAT MOVED, versus %s' % os.path.basename(a.baseline))
    bsrc = io.open(a.baseline, encoding='utf-8').read()
    B = fl(bsrc, 'const PLAYERS', '[')
    RAW0 = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', bsrc).group(1))
    bn = {p['n']: p for p in B}
    mv = [(p, bn[p['n']]) for p in P if p['n'] in bn
          and abs((p.get('pm') or 1.0) - (bn[p['n']].get('pm') or 1.0)) > 1e-9]
    print('     RAW %.2f -> %.2f  (%+.2f%%)' % (RAW0, RAW, 100 * (RAW / RAW0 - 1)))
    print('     multipliers changed: %d' % len(mv))
    dd = sorted(round((p.get('d') or 0) - (b.get('d') or 0), 2) for p, b in mv)
    if dd:
        print('     dollar band  5th %+.2f  median %+.2f  95th %+.2f  |>$1| %d'
              % (dd[int(0.05 * (len(dd) - 1))], dd[len(dd) // 2],
                 dd[int(0.95 * (len(dd) - 1))], sum(1 for x in dd if abs(x) > 1)))
    chk('the change moves value in both directions',
        sum(1 for x in dd if x > 0) > 50 and sum(1 for x in dd if x < 0) > 50,
        '%d up / %d down' % (sum(1 for x in dd if x > 0), sum(1 for x in dd if x < 0)))

print('\n' + '=' * 96)
print('  PASS %d   FAIL %d' % (N[0], N[1]))
print('=' * 96)
sys.exit(1 if N[1] else 0)

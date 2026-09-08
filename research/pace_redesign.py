# -*- coding: utf-8 -*-
"""Is the pace multiplier really double-counting missed games, and would a rate-based
comparison fix it? Read-only diagnostic — nothing is written.

THE CLAIM UNDER TEST. pm compares `pace` (a season TOTAL, scaled to 162) against `pc` (a full
healthy-season ceiling). For anyone who missed time that ratio is depressed by construction, no
matter how well he played when available. If true, pm is partly an availability penalty — and
availability is ALREADY priced in Hit% through `ir` and the durability fields. That double-count
is what the IL short-circuit was invented to paper over.

THE ALTERNATIVE. Compare a RATE to a RATE:
    rate          = ef / gp                      points per appearance, actual
    expected_rate = pc / role_games              points per appearance the ceiling implies
    w             = gp / (gp + k)                shrinkage, so six starts cannot earn a 1.50
    pm            = clamp(1 + A x w x (rate/expected_rate - 1), 0.50, 1.50)

role_games is derived from this league's own data (the 90th percentile of appearances by
position group) rather than assumed, so it is not a number anyone made up.
"""
import io, json, os, re, collections, math

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
CALC = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
TG, A = 143.0, 0.90                       # TEAM_GAMES and September absorption
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')


def find_literal(s, anchor, opener):
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
            if d == 0: return json.loads(s[j:k + 1])
    raise ValueError(anchor)


src = io.open(CALC, encoding='utf-8').read()
P = find_literal(src, 'const PLAYERS', '[')
RAW = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src).group(1))


def pit(p):
    return p.get('p') in ('SP', 'RP')


def peak_age(p):
    return 27 if pit(p) else 26


def expectation(p):
    e = p.get('eng') or {}
    pc, a = p.get('pc'), p.get('a')
    if a is not None and a < peak_age(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return pc / e['g']
    return pc


def allowed(p):
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


def grp(p):
    return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else
                                            ('C' if p.get('p') == 'C' else 'POS'))


# ─────────────────── 1. is pm correlated with games missed?
elig = [p for p in P if allowed(p) and p.get('pc') and (p.get('gp') or 0) > 0
        and p.get('pm') is not None and p.get('ef') is not None]
print('THE DOUBLE-COUNT, MEASURED')
print('  %d multiplier-eligible players with a games count' % len(elig))
print('  %-30s %5s %8s %8s   %s' % ('appearance rate vs team games', 'n', 'mean pm', 'at 1.00', 'mean pace/expectation'))
buck = collections.defaultdict(list)
for p in elig:
    ap = (p['gp'] or 0) / TG
    key = ('>90%  full-time' if ap > 0.90 else
           '70-90% mostly available' if ap > 0.70 else
           '40-70% missed real time' if ap > 0.40 else
           '<40%  missed most of it')
    buck[key].append(p)
for k in ('>90%  full-time', '70-90% mostly available', '40-70% missed real time', '<40%  missed most of it'):
    v = buck[k]
    if not v: continue
    pms = [p['pm'] for p in v]
    ratios = [(p.get('pace') or 0) / float(expectation(p)) for p in v if expectation(p)]
    print('  %-30s %5d %8.3f %7.0f%%   %.3f'
          % (k, len(v), sum(pms) / len(pms), 100.0 * sum(1 for x in pms if x == 1.0) / len(pms),
             sum(ratios) / len(ratios)))
print('  Read the last column: the ratio pm is built from falls with availability, which is the')
print('  double-count. A player who missed half a season cannot reach a full-season ceiling.\n')

# ─────────────────── 2. role_games, derived from the league's own data
print('ROLE APPEARANCE DENOMINATORS, derived not assumed')
role = {}
for g in ('SP', 'RP', 'C', 'POS'):
    gps = sorted((p['gp'] or 0) for p in P if grp(p) == g and (p.get('gp') or 0) > 0)
    if len(gps) < 12: continue
    p90 = gps[int(0.90 * (len(gps) - 1))]
    # scale that 143-game observation to a full 162
    role[g] = round(p90 * 162.0 / TG)
    print('  %-4s n=%-5d 90th pct appearances through %d team games = %-4d  ->  full season %d'
          % (g, len(gps), TG, p90, role[g]))
print()

# ─────────────────── 3. the rate-based multiplier
K = {'SP': 8, 'RP': 20, 'C': 40, 'POS': 40}
print('SHRINKAGE CONSTANTS  k = %s   (w = gp/(gp+k); pm reaches half its unshrunk')
print('  distance from 1.00 at k appearances)\n' % () if False else
      '  k = %s   w = gp/(gp+k), so a player reaches half his unshrunk distance from 1.00 at k appearances\n'
      % K)


def newpm(p):
    e = expectation(p)
    g = grp(p)
    rg = role.get(g)
    if not e or not rg or not (p.get('gp') or 0):
        return None
    rate = float(p['ef']) / float(p['gp'])
    exp_rate = float(e) / float(rg)
    if exp_rate <= 0:
        return None
    w = p['gp'] / float(p['gp'] + K[g])
    return max(0.50, min(1.50, round(1 + A * w * (rate / exp_rate - 1), 3)))


cand = [p for p in elig if newpm(p) is not None]
print('WHAT IT WOULD DO — %d eligible players' % len(cand))
old = [p['pm'] for p in cand]
new = [newpm(p) for p in cand]
print('  %-22s %8s %8s' % ('', 'current', 'proposed'))
print('  %-22s %8.3f %8.3f' % ('mean pm', sum(old) / len(old), sum(new) / len(new)))
print('  %-22s %8.0f%% %7.0f%%' % ('sitting at exactly 1.00',
                                   100.0 * sum(1 for x in old if x == 1.0) / len(old),
                                   100.0 * sum(1 for x in new if x == 1.0) / len(new)))
print('  %-22s %8.0f%% %7.0f%%' % ('pinned at a clamp',
                                   100.0 * sum(1 for x in old if x in (0.5, 1.5)) / len(old),
                                   100.0 * sum(1 for x in new if x in (0.5, 1.5)) / len(new)))
b2 = collections.defaultdict(list)
for p, n in zip(cand, new):
    ap = (p['gp'] or 0) / TG
    key = ('>90%' if ap > 0.90 else '70-90%' if ap > 0.70 else '40-70%' if ap > 0.40 else '<40%')
    b2[key].append(n)
print('\n  mean PROPOSED pm by availability — the flatness here is the point:')
for k in ('>90%', '70-90%', '40-70%', '<40%'):
    if b2[k]:
        print('    %-8s n=%-5d %.3f' % (k, len(b2[k]), sum(b2[k]) / len(b2[k])))

print('\n  the players we have been discussing')
NAMES = ('Luis Robert Jr.', 'Willi Castro', 'Shane McClanahan', 'Blake Snell', 'Logan Webb',
         'Gunnar Henderson', 'Jackson Holliday', 'Jesus Luzardo', 'Cade Cavalli', 'Matt Olson',
         'Pete Crow-Armstrong', 'Parker Messick', 'Dustin May', 'Bryce Elder')
print('  %-22s %-4s %-7s %5s %7s %8s %8s %9s %9s' %
      ('player', 'pos', 'IL', 'gp', 'rate', 'exp rate', 'w', 'pm now', 'pm new'))
for p in P:
    if p['n'] not in NAMES: continue
    n = newpm(p)
    if n is None:
        print('  %-22s %-4s %-7s   not multiplier-eligible (%s%s)'
              % (p['n'][:22], p.get('p'), str(p.get('il')), p.get('t'),
                 '/' + str(p.get('ph')) if p.get('ph') else ''))
        continue
    g = grp(p)
    rate = p['ef'] / float(p['gp'])
    er = expectation(p) / float(role[g])
    w = p['gp'] / float(p['gp'] + K[g])
    print('  %-22s %-4s %-7s %5d %7.1f %8.1f %8.2f %9.3f %9.3f'
          % (p['n'][:22], p.get('p'), str(p.get('il')), p['gp'], rate, er, w, p['pm'], n))

# ─────────────────── 4. blast radius
tot_old = sum(p['r'] for p in P if p.get('r'))
tot_new = 0
for p in P:
    if not p.get('r'):
        continue
    n = newpm(p) if (allowed(p) and p.get('pc') and (p.get('gp') or 0) and p.get('ef') is not None) else None
    if n is None or not p.get('pc') or p.get('h') is None:
        tot_new += p['r']
    else:
        tot_new += round(p['pc'] * n * p['h'])
pool_old = [p['r'] for p in P if p.get('eid') is not None and (p.get('r') or 0) > 0]
raw_old = sum(pool_old) / len(pool_old)
pool_new = []
for p in P:
    if p.get('eid') is None:
        continue
    n = newpm(p) if (allowed(p) and p.get('pc') and (p.get('gp') or 0) and p.get('ef') is not None) else None
    r = p['r'] if (n is None or not p.get('pc') or p.get('h') is None) else round(p['pc'] * n * p['h'])
    if (r or 0) > 0:
        pool_new.append(r)
raw_new = sum(pool_new) / len(pool_new)
print('\nBLAST RADIUS')
print('  board RA        %s -> %s  (%+.1f%%)' % (format(tot_old, ',d'), format(tot_new, ',d'),
                                                 100.0 * (tot_new - tot_old) / tot_old))
print('  RAW_PER_DOLLAR  %.2f -> %.2f  (%+.1f%%)' % (raw_old, raw_new,
                                                     100.0 * (raw_new - raw_old) / raw_old))
print('  every dynasty dollar re-bases, so this is a build to run deliberately, not a hotfix.')

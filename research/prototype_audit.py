# -*- coding: utf-8 -*-
"""Adversarial audit of the rate-based prototype. Looking for the failure mode that §20.10 and
§20.30(B) already fixed once in the TOTAL domain and that could easily reappear in the RATE
domain: a young player judged against a ceiling he is not meant to reach yet.

expectation() carries the §20.30(B) fix — Pure/eng.g for a pre-peak PRODUCTION-BASIS player.
A pre-peak player who is NOT production-basis, or who has no eng.g, is still compared against
the full projected peak. In the total domain the §20.10 tier/phase gate hid most of those,
because Honeymoon and Book T3 never get a multiplier. The question is whether any survive into
Established phase and get punished for being 21.
"""
import io, json, os, re, collections

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
PROTO = YEAR + 'GN_pm_rate_prototype_2026-09-07/'
ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {'SP': 8, 'RP': 20, 'C': 40, 'POS': 40}


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


src = io.open(LIVE, encoding='utf-8').read()
BASE = find_literal(src, 'const PLAYERS', '[')
RAW_A = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src).group(1))
PC_ = json.load(open(PROTO + 'PLAYERS_scenarioC.json'))
RPT = json.load(open(PROTO + 'report.json'))
RAW_C = RPT['RAW_scenarioC']
by = {p['n']: p for p in PC_}


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))


def expectation(p):
    e = p.get('eng') or {}
    pc, a = p.get('pc'), p.get('a')
    if a is not None and a < peak_age(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return pc / e['g'], 'pc/g  (20.30 B)'
    return pc, 'pc'


def moved(p):
    b = next(q for q in BASE if q['n'] == p['n'])
    return (p.get('r') or 0) - (b.get('r') or 0), b


# ── 1. of the eligible players who got a rate-based multiplier, who is PRE-PEAK?
rated = [p for p in PC_ if str(p.get('_x', '')) or True]
rated = [p for p in PC_ if abs((p.get('pm') or 1) - 1) > 1e-9 or True]
elig = []
for p in PC_:
    b = next(q for q in BASE if q['n'] == p['n'])
    e, kind = expectation(p)
    if not e or (p.get('gp') or 0) == 0 or not p.get('pc'):
        continue
    t = str(p.get('t') or '')
    if not (t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')):
        continue
    a = p.get('a')
    elig.append(dict(p=p, b=b, e=e, kind=kind, a=a,
                     pre=(a is not None and a < peak_age(p)),
                     dd=round((p.get('d') or 0) - (b.get('d') or 0), 2)))

print('ELIGIBLE, RATE-JUDGED PLAYERS: %d' % len(elig))
pre = [x for x in elig if x['pre']]
print('  pre-peak (younger than %s): %d' % ('26 hitters / 27 pitchers', len(pre)))
kinds = collections.Counter(x['kind'] for x in pre)
print('  of those, the denominator used:')
for k, n in kinds.items():
    print('     %-20s %4d' % (k, n))
exposed = [x for x in pre if x['kind'] == 'pc']
print('\n  EXPOSED — pre-peak but judged against the FULL projected peak: %d' % len(exposed))
if exposed:
    print('  %-24s %-22s %-4s %-3s %-6s %-6s %8s %8s %7s' %
          ('player', 'org', 'pos', 'age', 'basis', 'phase', 'pm now', 'pm new', '$ delta'))
    for x in sorted(exposed, key=lambda q: q['dd'])[:14]:
        p, b = x['p'], x['b']
        print('  %-24s %-22s %-4s %-3s %-6s %-6s %8.3f %8.3f %+7.2f'
              % (p['n'][:24], str(p.get('o') or 'FA')[:22], p.get('p'), p.get('a'),
                 (p.get('eng') or {}).get('b'), p.get('ph') or '', b.get('pm') or 1,
                 p.get('pm') or 1, x['dd']))
    hurt = [x for x in exposed if x['dd'] < -0.25]
    print('\n  of the exposed, %d lose more than $0.25 — these are the ones to look at' % len(hurt))

# ── 2. the twelve biggest fallers, fully decomposed
print('\nTHE TWELVE BIGGEST FALLERS, DECOMPOSED')
print('  %-22s %-4s %-3s %-6s %-7s %6s %7s %8s %8s %7s' %
      ('player', 'pos', 'age', 'basis', 'IL', 'gp', 'rate', 'exp rate', 'pm new', '$'))
for x in sorted(elig, key=lambda q: q['dd'])[:12]:
    p = x['p']
    g = grp(p)
    rate = (p['ef'] or 0) / float(p['gp'])
    er = x['e'] / float(ROLE_GAMES[g])
    print('  %-22s %-4s %-3s %-6s %-7s %6d %7.1f %8.1f %8.3f %+7.2f'
          % (p['n'][:22], p.get('p'), p.get('a'), (p.get('eng') or {}).get('b'),
             str(p.get('il')), p['gp'], rate, er, p.get('pm') or 1, x['dd']))

# ── 3. the twelve biggest risers
print('\nTHE TWELVE BIGGEST RISERS, DECOMPOSED')
print('  %-22s %-4s %-3s %-6s %-7s %6s %7s %8s %8s %7s' %
      ('player', 'pos', 'age', 'basis', 'IL', 'gp', 'rate', 'exp rate', 'pm new', '$'))
for x in sorted(elig, key=lambda q: -q['dd'])[:12]:
    p = x['p']
    g = grp(p)
    rate = (p['ef'] or 0) / float(p['gp'])
    er = x['e'] / float(ROLE_GAMES[g])
    print('  %-22s %-4s %-3s %-6s %-7s %6d %7.1f %8.1f %8.3f %+7.2f'
          % (p['n'][:22], p.get('p'), p.get('a'), (p.get('eng') or {}).get('b'),
             str(p.get('il')), p['gp'], rate, er, p.get('pm') or 1, x['dd']))

# ── 4. does the multiplier still correlate with anything it should not?
print('\nCORRELATION CHECKS (scenario C)')
import math


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    if sx == 0 or sy == 0: return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


gp = [x['p']['gp'] for x in elig]
pmA = [x['b'].get('pm') or 1 for x in elig]
pmC = [x['p'].get('pm') or 1 for x in elig]
ages = [x['a'] for x in elig if x['a'] is not None]
pmC_a = [x['p'].get('pm') or 1 for x in elig if x['a'] is not None]
print('  pm vs games played   baseline %+.3f    scenario C %+.3f   (want ~0 in C)'
      % (corr(gp, pmA), corr(gp, pmC)))
print('  pm vs age            baseline %+.3f    scenario C %+.3f   (want ~0; negative means young players punished)'
      % (corr([x['a'] for x in elig if x['a'] is not None], [x['b'].get('pm') or 1 for x in elig if x['a'] is not None]),
         corr(ages, pmC_a)))
onil = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')
il = [1.0 if str(x['p'].get('il')) in onil else 0.0 for x in elig]
print('  pm vs on-the-IL flag baseline %+.3f    scenario C %+.3f'
      % (corr(il, pmA), corr(il, pmC)))

# ── 5. dollar dispersion — is anything absurd?
dds = sorted(x['dd'] for x in elig)
print('\nDOLLAR MOVE DISTRIBUTION across the %d eligible' % len(elig))
for q, lbl in ((0.0, 'min'), (0.05, '5th'), (0.25, '25th'), (0.5, 'median'),
               (0.75, '75th'), (0.95, '95th'), (1.0, 'max')):
    print('  %-8s %+6.2f' % (lbl, dds[min(len(dds) - 1, int(q * (len(dds) - 1)))]))
print('  players moving more than $1.00 either way: %d'
      % sum(1 for d in dds if abs(d) > 1.0))

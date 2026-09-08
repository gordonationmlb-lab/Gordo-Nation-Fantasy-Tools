# -*- coding: utf-8 -*-
"""Re-audit after the two fixes. Same adversarial questions, asked of the corrected prototype."""
import io, json, os, re, collections, math

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
PROTO = YEAR + 'GN_pm_rate_prototype_2026-09-07/'
ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {g: int(round(0.45 * n)) for g, n in ROLE_GAMES.items()}


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


src = io.open(LIVE, encoding='utf-8').read()
BASE = fl(src, 'const PLAYERS', '[')
RAW_A = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src).group(1))
PCn = json.load(open(PROTO + 'PLAYERS_scenarioC.json'))
RAW_C = json.load(open(PROTO + 'report.json'))['RAW_scenarioC']


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)


def expectation(p):
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


rows = []
for i, p in enumerate(PCn):
    b = BASE[i]
    assert p['n'] == b['n']
    if abs((p.get('pm') or 1) - (b.get('pm') or 1)) < 1e-9 and (p.get('r') or 0) == (b.get('r') or 0):
        continue
    rows.append(dict(p=p, b=b, dd=round((p.get('d') or 0) - (b.get('d') or 0), 2)))
print('movers: %d' % len(rows))

print('\nQ1 — any tool-basis ceiling still carrying a multiplier?')
leak = [r for r in rows if basis(r['p']) == 'tool' and abs((r['p'].get('pm') or 1) - 1) > 1e-9]
print('    %s' % ('NONE — the gate holds' if not leak else '%d LEAKS: %s' % (len(leak), [r['p']['n'] for r in leak[:5]])))

print('\nQ2 — any pre-peak player judged against a full projected peak?')
exposed = [r for r in rows if prepeak(r['p']) and abs((r['p'].get('pm') or 1) - 1) > 1e-9
           and expectation(r['p']) == r['p'].get('pc')]
print('    %d such players carry a multiplier' % len(exposed))
for r in sorted(exposed, key=lambda q: q['dd'])[:6]:
    p = r['p']
    print('       %-24s %-4s age %-3s basis %-5s pm %.3f  $ %+.2f'
          % (p['n'][:24], p.get('p'), p.get('a'), str(basis(p)), p.get('pm') or 1, r['dd']))
if not exposed:
    print('       none — every pre-peak multiplier now uses the 20.30(B) denominator')

print('\nQ3 — the ten biggest fallers, decomposed')
print('    %-22s %-4s %-3s %-5s %-7s %5s %7s %8s %7s %7s' %
      ('player', 'pos', 'age', 'basis', 'IL', 'gp', 'rate', 'exp rate', 'pm', '$'))
for r in sorted(rows, key=lambda q: q['dd'])[:10]:
    p = r['p']; g = grp(p)
    rate = (p.get('ef') or 0) / float(p['gp']) if p.get('gp') else 0
    er = expectation(p) / float(ROLE_GAMES[g]) if p.get('pc') else 0
    print('    %-22s %-4s %-3s %-5s %-7s %5s %7.1f %8.1f %7.3f %+7.2f'
          % (p['n'][:22], p.get('p'), p.get('a'), str(basis(p)), str(p.get('il')),
             p.get('gp'), rate, er, p.get('pm') or 1, r['dd']))

print('\nQ4 — correlations the multiplier should NOT have')


def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n); sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return 0.0 if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')
el = [(b, p) for b, p in zip(BASE, PCn)
      if abs((p.get('pm') or 1) - 1) > 1e-9 or abs((b.get('pm') or 1) - 1) > 1e-9]
gp = [p.get('gp') or 0 for _b, p in el]
print('    pm vs games played    baseline %+.3f   prototype %+.3f'
      % (corr(gp, [b.get('pm') or 1 for b, _p in el]), corr(gp, [p.get('pm') or 1 for _b, p in el])))
il = [1.0 if str(p.get('il')) in ONIL else 0.0 for _b, p in el]
print('    pm vs on-the-IL       baseline %+.3f   prototype %+.3f'
      % (corr(il, [b.get('pm') or 1 for b, _p in el]), corr(il, [p.get('pm') or 1 for _b, p in el])))
ag = [(b, p) for b, p in el if p.get('a') is not None]
print('    pm vs age             baseline %+.3f   prototype %+.3f'
      % (corr([p['a'] for _b, p in ag], [b.get('pm') or 1 for b, _p in ag]),
         corr([p['a'] for _b, p in ag], [p.get('pm') or 1 for _b, p in ag])))

print('\nQ5 — dollar move distribution')
dds = sorted(r['dd'] for r in rows)
for q, lbl in ((0.0, 'min'), (0.05, '5th'), (0.25, '25th'), (0.5, 'median'),
               (0.75, '75th'), (0.95, '95th'), (1.0, 'max')):
    print('    %-8s %+6.2f' % (lbl, dds[min(len(dds) - 1, int(q * (len(dds) - 1)))]))
print('    moving more than $1.00 either way: %d' % sum(1 for d in dds if abs(d) > 1.0))

print('\nQ6 — is the live build still untouched?')
h = io.open(LIVE, encoding='utf-8').read()
print('    RAW in the live app: %s   GN_BUILD: %s'
      % (re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', h).group(1),
         re.search(r"GN_BUILD\s*=\s*'([^']+)'", h).group(1)))
print('    %s' % ('unchanged' if abs(float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', h).group(1)) - RAW_A) < 1e-9
                  else 'CHANGED — investigate'))

# -*- coding: utf-8 -*-
"""Do the two proposed pace formulas differ from the one v50.21 already runs?

CURRENT   pace = ef x F,  F = 162 / TEAM_GAMES                       (one league-wide scalar)
OPTION 1  pace = ef + (ef/gp) x G_rem                                (assume 100% forward availability)
OPTION 2  pace = ef + (ef/gp) x (G_rem x gp/TG)                      (forward availability = past)

Read-only. Nothing is written and no build is touched.
"""
import io, json, os, re, collections

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
CALC = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
TG = 143.0                      # TEAM_GAMES, the v50.21 run constant
G_REM = 162.0 - TG              # 19
F = 162.0 / TG                  # 1.1329


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
print('v50.21   TEAM_GAMES %.0f   games remaining %.0f   F = %.4f   RAW %.2f' % (TG, G_REM, F, RAW))

live = [p for p in P if p.get('ef') is not None and (p.get('gp') or 0) > 0 and p.get('pace') is not None]
print('%d of %d records carry both a season total and a games-played count\n' % (len(live), len(P)))

# ─────────────────────────────────────────── the algebra, checked on real rows
d1 = d2 = 0.0
rows = []
for p in live:
    ef, gp = float(p['ef']), float(p['gp'])
    cur = round(ef * F)
    o1 = round(ef + (ef / gp) * G_REM)
    o2 = round(ef + (ef / gp) * (G_REM * gp / TG))
    d1 = max(d1, abs(o1 - cur)); d2 = max(d2, abs(o2 - cur))
    rows.append((p, ef, gp, cur, o1, o2))
print('OPTION 2 against what the build already computes')
print('  largest absolute difference across %d players : %.0f point%s'
      % (len(rows), d2, '' if d2 == 1 else 's'))
print('  ...because the gp terms cancel:  ef + (ef/gp)(G_rem x gp/TG) = ef(1 + G_rem/TG) = ef x 162/TG = ef x F')
print('  Option 2 IS the current formula, written the long way round.\n')

print('OPTION 1 against the same baseline')
print('  largest absolute difference : %.0f points' % d1)
buck = collections.defaultdict(list)
for p, ef, gp, cur, o1, o2 in rows:
    ap = gp / TG
    key = ('everyday hitter  >85%' if ap > 0.85 else
           'part-time hitter 50-85%' if ap > 0.50 else
           'reliever / platoon 25-50%' if ap > 0.25 else
           'starting pitcher <25%')
    if cur > 0:
        buck[key].append(100.0 * (o1 - cur) / cur)
print('  %-28s %6s %10s' % ('appearance rate', 'n', 'Option 1 vs current'))
for k in ('everyday hitter  >85%', 'part-time hitter 50-85%', 'reliever / platoon 25-50%',
          'starting pitcher <25%'):
    v = buck[k]
    if v:
        print('  %-28s %6d %+9.1f%%' % (k, len(v), sum(v) / len(v)))

print('\n  worked examples')
NAMES = ('Pete Crow-Armstrong', 'Matt Olson', 'Jesus Luzardo', 'Parker Messick', 'Blake Snell',
         'Cade Smith', 'Louis Varland', 'Luis Robert Jr.')
print('  %-22s %-4s %5s %6s %7s %9s %9s %9s' % ('player', 'pos', 'gp', 'ef', 'app%', 'current', 'option 1', 'option 2'))
for p, ef, gp, cur, o1, o2 in rows:
    if p['n'] in NAMES:
        print('  %-22s %-4s %5.0f %6.0f %6.0f%% %9.0f %9.0f %9.0f'
              % (p['n'][:22], p.get('p'), gp, ef, 100 * gp / TG, cur, o1, o2))
print('\n  Option 1 credits every player with appearing in all %.0f remaining TEAM games. That is'
      % G_REM)
print('  right for an everyday hitter and badly wrong for a pitcher: a starter appears about once')
print('  every five team games, so nineteen team games left means about four more starts, not nineteen.')

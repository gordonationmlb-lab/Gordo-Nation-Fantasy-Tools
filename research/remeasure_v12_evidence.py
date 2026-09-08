# -*- coding: utf-8 -*-
"""Re-measure the five claims the fact check rejected, on pools that can be stated in the
methodology and reproduced from it.

WHY THEY FAILED
  1/2. AVAILABILITY WAS DEFINED ROLE-BLIND. pace_redesign.py bucketed on gp / TEAM_GAMES, so a
       starter with a full 30-start season reads as 21% "available" and every SP lands in the
       "<40%" bucket. That confounds role with health, which is exactly the thing being measured.
       The role-adjusted definition — appearances / (ROLE_GAMES x TEAM_GAMES / 162), i.e. the
       fraction of his own role's workload to date — is what "availability" means, and it makes
       the finding stronger, not weaker.
  3.   BASALLO'S -$1.38 was computed at the pre-calibration k (C = 40). At the shipped k (C = 54)
       the ungated loss is smaller. The draft must quote the figure at the constants it ships.
  4.   "246 FORCED TO 1.00" was not reproducible from any stated pool. The claim's actual content
       is "players the old rules held at 1.00 who the new rules price", which is directly
       countable.
  5.   CLAMP SATURATION 15% -> 1% mixed pools: the 15% counted players sitting at exactly 1.00 in
       its denominator, the 1% did not. Both formulas are scored here over the same pool.
"""
import io, json, os, re, math, collections

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
PROTO = YEAR + 'GN_pm_rate_prototype_2026-09-07/'
ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {'SP': 15, 'RP': 31, 'C': 54, 'POS': 69}
MIN_APP = {'SP': 3, 'RP': 8, 'C': 15, 'POS': 15}
ABSORB, PC_MIN, TG = 0.90, 300, 143.0
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')


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
BASE = fl(src, 'const PLAYERS', '[')
RAW_A = float(re.search(r'RAW_PER_DOLLAR\s*=\s*([0-9.]+)', src).group(1))
PC_ = json.load(open(PROTO + 'PLAYERS_scenarioC.json'))
RPT = json.load(open(PROTO + 'report.json'))
RAW_C = RPT['RAW_scenarioC']


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)
def tierok(p):
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


def expectation(p):
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


def avail(p):
    """Fraction of his OWN ROLE's workload to date. Role-adjusted, so role does not masquerade
    as health: 33 starts is a full SP season, 154 games a full position-player season."""
    return min(1.0, (p.get('gp') or 0) / (ROLE_GAMES[grp(p)] * TG / 162.0))


BANDS = ((0.90, '>90%'), (0.70, '70-90%'), (0.40, '40-70%'), (0.0, '<40%'))


def band(p):
    a = avail(p)
    for lo, lbl in BANDS:
        if a >= lo: return lbl
    return '<40%'


# ════════════════════════════ the scoring pool, stated once and used for everything
def scored(p):
    """Eligible under the v50.22 gates: tier/phase, production-established ceiling, a growth
    factor if pre-peak, Pure >= 300, and the role minimum appearances."""
    if not tierok(p): return False
    if basis(p) == 'tool': return False
    if (p.get('pc') or 0) < PC_MIN: return False
    if p.get('ef') is None or (p.get('gp') or 0) < MIN_APP[grp(p)]: return False
    if basis(p) == 'prod' and prepeak(p) and not ((p.get('eng') or {}).get('g') and p['eng']['g'] > 1):
        return False
    return True


POOL = [(b, c) for b, c in zip(BASE, PC_) if scored(b)]
print('SCORING POOL: %d players eligible under the v50.22 gates' % len(POOL))
print('  (tier/phase + production-basis ceiling + growth factor if pre-peak + Pure>=300 + min appearances)')


def pm_total(p):
    """What the v11 TOTAL form assigns, with the IL short-circuit NOT applied — so the two
    formulas are compared as formulas, not as formula-plus-workaround."""
    pace = round((p.get('ef') or 0) * 162.0 / TG)
    e = expectation(p)
    if not e: return 1.0
    return round(max(0.50, min(1.50, 1 + ABSORB * (pace / float(e) - 1))), 3)


def pm_rate(p):
    g = grp(p)
    rate = (p.get('ef') or 0) / float(p['gp'])
    er = expectation(p) / float(ROLE_GAMES[g])
    w = p['gp'] / float(p['gp'] + K_SHRINK[g])
    return round(max(0.50, min(1.50, 1 + ABSORB * w * (rate / er - 1))), 3)


# ════════════════════════════ 1 & 2. the availability gradient, both formulas, same pool
print('\n' + '=' * 92)
print('1 & 2. THE AVAILABILITY GRADIENT — both formulas over the same %d players' % len(POOL))
print('=' * 92)
print('  %-9s %6s   %-24s %-24s' % ('band', 'n', 'TOTAL form (v11)', 'RATE form (v50.22)'))
print('  %-9s %6s   %10s %13s %10s %13s'
      % ('', '', 'ratio', 'mean pm', 'ratio', 'mean pm'))
rows = {}
for lo, lbl in BANDS:
    v = [b for b, _c in POOL if band(b) == lbl]
    if not v: continue
    ratio_t = sum(round(p['ef'] * 162.0 / TG) / float(expectation(p)) for p in v) / len(v)
    pm_t = sum(pm_total(p) for p in v) / len(v)
    g = grp
    ratio_r = sum(((p['ef'] / float(p['gp'])) /
                   (expectation(p) / float(ROLE_GAMES[grp(p)]))) for p in v) / len(v)
    pm_r = sum(pm_rate(p) for p in v) / len(v)
    rows[lbl] = (len(v), ratio_t, pm_t, ratio_r, pm_r)
    print('  %-9s %6d   %10.3f %13.3f %10.3f %13.3f' % (lbl, len(v), ratio_t, pm_t, ratio_r, pm_r))
hi, lo_ = rows['>90%'], rows['<40%']
print('\n  TOTAL form: the ratio runs %.3f at full availability and %.3f below 40%% — a %.3f spread.'
      % (hi[1], lo_[1], hi[1] - lo_[1]))
print('  RATE form:  %.3f and %.3f — a %.3f spread. The gradient the multiplier should not have'
      % (hi[3], lo_[3], hi[3] - lo_[3]))
print('  shrinks by %.0fx.' % ((hi[1] - lo_[1]) / max(1e-9, abs(hi[3] - lo_[3]))))
print('\n  mean multiplier by band, TOTAL %s' % ' / '.join('%.3f' % rows[l][2] for _x, l in BANDS if l in rows))
print('  mean multiplier by band, RATE  %s' % ' / '.join('%.3f' % rows[l][4] for _x, l in BANDS if l in rows))

il = [1.0 if str(b.get('il')) in ONIL else 0.0 for b, _c in POOL]


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n); sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return 0.0 if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


print('\n  correlation of the multiplier with being on the IL, same pool:')
print('     TOTAL form %+.3f     RATE form %+.3f'
      % (corr(il, [pm_total(b) for b, _c in POOL]), corr(il, [pm_rate(b) for b, _c in POOL])))
print('  correlation with appearances:')
print('     TOTAL form %+.3f     RATE form %+.3f'
      % (corr([b['gp'] for b, _c in POOL], [pm_total(b) for b, _c in POOL]),
         corr([b['gp'] for b, _c in POOL], [pm_rate(b) for b, _c in POOL])))
print('\n  AS SHIPPED (v11 formula plus the IL short-circuit, versus the prototype as built):')
elx = [(b, c) for b, c in zip(BASE, PC_)
       if abs((c.get('pm') or 1) - 1) > 1e-9 or abs((b.get('pm') or 1) - 1) > 1e-9]
ilx = [1.0 if str(c.get('il')) in ONIL else 0.0 for _b, c in elx]
print('     live build %+.3f     prototype %+.3f'
      % (corr(ilx, [b.get('pm') or 1 for b, _c in elx]), corr(ilx, [c.get('pm') or 1 for _b, c in elx])))

# ════════════════════════════ 5. clamp saturation, same pool, both formulas
print('\n' + '=' * 92)
print('5. CLAMP SATURATION — both formulas over the same pool')
print('=' * 92)
t = [pm_total(b) for b, _c in POOL]; r = [pm_rate(b) for b, _c in POOL]
for lbl, v in (('TOTAL form (v11)', t), ('RATE form (v50.22)', r)):
    print('  %-20s at 0.50: %4.1f%%   at 1.50: %4.1f%%   at either clamp: %4.1f%%'
          % (lbl, 100.0 * v.count(0.5) / len(v), 100.0 * v.count(1.5) / len(v),
             100.0 * sum(1 for x in v if x in (0.5, 1.5)) / len(v)))
print('  -> the draft should read "%.0f%% to %.0f%%"'
      % (100.0 * sum(1 for x in t if x in (0.5, 1.5)) / len(t),
         100.0 * sum(1 for x in r if x in (0.5, 1.5)) / len(r)))

# ════════════════════════════ 4. what the old rules held at 1.00 and the new rules price
print('\n' + '=' * 92)
print('4. PLAYERS THE OLD RULES HELD AT 1.00 THAT THE NEW RULES PRICE')
print('=' * 92)
held = [(b, c) for b, c in zip(BASE, PC_)
        if abs((b.get('pm') or 1) - 1) < 1e-9 and abs((c.get('pm') or 1) - 1) > 1e-9]
print('  live pm exactly 1.000 -> prototype assigns a multiplier: %d players' % len(held))
onil_held = sum(1 for b, _c in held if str(b.get('il')) in ONIL)
print('     of those, %d are on an IL designation now (the short-circuit\'s own doing)' % onil_held)
print('     the other %d were parked by ALLOW_NEW_PM after a past clearance' % (len(held) - onil_held))
print('  -> the draft should read "%d players" (of which %d currently on an IL designation)'
      % (len(held), onil_held))

# ════════════════════════════ 3. Basallo at the shipped constants
print('\n' + '=' * 92)
print('3. THE TOOL-BASIS GATE, SIZED AT THE SHIPPED CONSTANTS')
print('=' * 92)
tool = [p for p in BASE if tierok(p) and (p.get('pc') or 0) >= PC_MIN
        and (p.get('gp') or 0) >= MIN_APP[grp(p)] and basis(p) == 'tool']
print('  tool-basis players clearing tier/phase/Pure/appearances: %d (%d pre-peak)'
      % (len(tool), sum(1 for p in tool if prepeak(p))))
print('  %-24s %-4s %-3s %8s %9s %9s %8s %8s'
      % ('player', 'pos', 'age', 'gp', 'rate', 'exp rate', 'pm', '$ at risk'))
worst = []
for p in sorted(tool, key=lambda q: -(q.get('pc') or 0)):
    if (p.get('gp') or 0) < MIN_APP[grp(p)] or p.get('ef') is None: continue
    g = grp(p)
    rate = p['ef'] / float(p['gp']); er = expectation(p) / float(ROLE_GAMES[g])
    pmx = pm_rate(p)
    dollars = round((p['pc'] * (pmx - 1.0) * (p.get('h') or 0)) / RAW_C, 2)
    worst.append((dollars, p['n'], p, pmx, rate, er))
for dollars, n, p, pmx, rate, er in sorted(worst)[:8]:
    print('  %-24s %-4s %-3s %8d %9.1f %9.1f %8.3f %+8.2f'
          % (n[:24], p.get('p'), p.get('a'), p['gp'], rate, er, pmx, dollars))
b0 = sorted(worst)[0]
print('\n  worst exposure at the shipped k: %s, $%+.2f' % (b0[1], b0[0]))
print('  -> the draft should quote %s at $%+.2f, not the pre-calibration figure' % (b0[1], b0[0]))

# ════════════════════════════ free-agent aggregate, for the 20.33 claim
print('\n' + '=' * 92)
print('ORG SHARES — clubs individually, free agency in aggregate')
print('=' * 92)
agg = collections.defaultdict(lambda: [0.0, 0.0])
CLUBS = ('River Cats', 'Kansas Sunflower Seeds', 'KC Gray Hotdogs', 'High Cheddar',
         'C-Town Liquors', 'Balking Dead', 'Dirty Spikes', 'MidwestBears')
for b, c in zip(BASE, PC_):
    o = b.get('o') or ''
    key = o if o in CLUBS else 'Free agency (all)'
    agg[key][0] += (b.get('d') or 0); agg[key][1] += (c.get('d') or 0)
tA = sum(v[0] for v in agg.values()); tC = sum(v[1] for v in agg.values())
print('  %-24s %9s %9s %8s %9s' % ('', 'A $', 'C $', 'delta', 'share pp'))
mx = 0.0
for o, v in sorted(agg.items(), key=lambda kv: -kv[1][0]):
    sh = 100 * v[1] / tC - 100 * v[0] / tA
    if o in CLUBS: mx = max(mx, abs(sh))
    print('  %-24s %9.2f %9.2f %+8.2f %+9.2f' % (o[:24], v[0], v[1], v[1] - v[0], sh))
print('\n  largest club share move: %.2f pp' % mx)

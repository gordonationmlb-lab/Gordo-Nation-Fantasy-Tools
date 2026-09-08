# -*- coding: utf-8 -*-
"""Every number and named player in the v12 draft, checked against the live board and the
prototype output. A methodology that misstates its own evidence is worse than one that omits it.

    python3 factcheck_methodology_v12.py
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
ABSORB, PC_MIN, TEAM_GAMES = 0.90, 300, 143.0
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')

OK = [0, 0]


def chk(claim, cond, detail=''):
    OK[0 if cond else 1] += 1
    print('  [%s] %-58s %s' % ('PASS' if cond else 'FAIL', claim, detail))


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
PB_ = json.load(open(PROTO + 'PLAYERS_scenarioB.json'))
RPT = json.load(open(PROTO + 'report.json'))
bn = {p['n']: p for p in BASE}
cn = {p['n']: p for p in PC_}


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


def dd(name):
    b, c = bn.get(name), cn.get(name)
    if not b or not c: return None
    return round((c.get('d') or 0) - (b.get('d') or 0), 2)


print('=' * 96)
print('SECTION 13 — the formula and its constants')
print('=' * 96)
for g in ('SP', 'RP', 'C', 'POS'):
    chk('k(%s) = round(0.45 x ROLE_GAMES) = %d' % (g, K_SHRINK[g]),
        int(round(0.45 * ROLE_GAMES[g])) == K_SHRINK[g],
        '0.45 x %d = %.2f' % (ROLE_GAMES[g], 0.45 * ROLE_GAMES[g]))
chk('ROLE_GAMES matches the prototype report', RPT['ROLE_GAMES'] == ROLE_GAMES, str(RPT['ROLE_GAMES']))
chk('MIN_APP matches the prototype report', RPT['MIN_APP'] == MIN_APP, str(RPT['MIN_APP']))
chk('absorption 0.90 (September)', abs(RPT['ABSORB'] - 0.90) < 1e-9)
chk('TEAM_GAMES flat at 143', abs(RPT['TEAM_GAMES'] - 143.0) < 1e-9)

print('\n' + '=' * 96)
print('SECTION 13 — "WHY THIS REPLACED THE TOTAL FORM": the measured double count')
print('=' * 96)
# availability bands on the BASELINE pace/expectation ratio
bands = [(0.90, 9.99, '>90%'), (0.70, 0.90, '70-90%'), (0.40, 0.70, '40-70%'), (0.0, 0.40, '<40%')]


def corr(xs, ys):
    n = len(xs)
    if n < 3: return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n); sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return 0.0 if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


def is_import(p):
    """20.15 lock is precedence step 1 — marker lives in the append-only notes log."""
    return bool(re.search(r'IMPORT-PACE', p.get('notes') or '', re.I))


def retired_by_rule(p):
    """19.6 ratchet / 20.12 recency floor already banked the season — precedence step 2."""
    return bool((p.get('eng') or {}).get('rch')) or 'RECENCY FLOOR' in (p.get('notes') or '')


def scored(p):
    """The population EITHER formula prices: precedence steps 1-2 remove imports and
    rule-retired players before the eligibility gates are reached at all."""
    if is_import(p) or retired_by_rule(p): return False
    if not tierok(p): return False
    if basis(p) == 'tool': return False
    if (p.get('pc') or 0) < PC_MIN: return False
    if p.get('ef') is None or (p.get('gp') or 0) < MIN_APP[grp(p)]: return False
    if basis(p) == 'prod' and prepeak(p) and not ((p.get('eng') or {}).get('g') and p['eng']['g'] > 1):
        return False
    return True


elig_b = [p for p in BASE if scored(p)]
chk('the stated scoring pool is 581 players', len(elig_b) == 581, 'counted %d' % len(elig_b))
rat = collections.defaultdict(list)
for p in elig_b:
    g = grp(p)
    avail = min(1.0, p['gp'] / float(ROLE_GAMES[g] * TEAM_GAMES / 162.0))
    pace = round(p['ef'] * 162.0 / TEAM_GAMES)
    r = pace / float(expectation(p)) if expectation(p) else 0
    for lo, hi, lbl in bands:
        if lo <= avail < hi or (lbl == '>90%' and avail >= 0.90):
            rat[lbl].append(r); break
means = {k: sum(v) / len(v) for k, v in rat.items() if v}
print('    baseline pace/expectation by availability band:')
for _lo, _hi, lbl in bands:
    if lbl in means: print('       %-8s n=%-4d mean %.3f' % (lbl, len(rat[lbl]), means[lbl]))
chk('total-form ratio 0.972 above 90%% availability', abs(means.get('>90%', 0) - 0.972) < 0.005,
    'measured %.3f' % means.get('>90%', 0))
chk('total-form ratio 0.229 below 40%% availability', abs(means.get('<40%', 0) - 0.229) < 0.005,
    'measured %.3f' % means.get('<40%', 0))
chk('a spread of 0.744', abs((means.get('>90%', 0) - means.get('<40%', 0)) - 0.744) < 0.005,
    'measured %.3f' % (means.get('>90%', 0) - means.get('<40%', 0)))


el = [(b, c) for b, c in zip(BASE, PC_)
      if abs((c.get('pm') or 1) - 1) > 1e-9 or abs((b.get('pm') or 1) - 1) > 1e-9]
il = [1.0 if str(c.get('il')) in ONIL else 0.0 for _b, c in el]
cA = corr(il, [b.get('pm') or 1 for b, _c in el])
cC = corr(il, [c.get('pm') or 1 for _b, c in el])
chk('IL correlation baseline +0.246', abs(cA - 0.246) < 0.01, 'measured %+.3f' % cA)
chk('IL correlation prototype -0.064', abs(cC + 0.064) < 0.01, 'measured %+.3f' % cC)

# both formulas, mean multiplier by band, over the SAME stated pool
def pm_total(p):
    e = expectation(p)
    if not e: return 1.0
    return round(max(0.5, min(1.5, 1 + ABSORB * (round(p['ef'] * 162.0 / TEAM_GAMES) / float(e) - 1))), 3)


def pm_rate(p):
    g = grp(p)
    rate = p['ef'] / float(p['gp']); er = expectation(p) / float(ROLE_GAMES[g])
    w = p['gp'] / float(p['gp'] + K_SHRINK[g])
    return round(max(0.5, min(1.5, 1 + ABSORB * w * (rate / er - 1))), 3)


gT = collections.defaultdict(list); gR = collections.defaultdict(list); gRr = collections.defaultdict(list)
for p in elig_b:
    g = grp(p)
    avail = min(1.0, p['gp'] / float(ROLE_GAMES[g] * TEAM_GAMES / 162.0))
    for lo, hi, lbl in bands:
        if lo <= avail < hi or (lbl == '>90%' and avail >= 0.90):
            gT[lbl].append(pm_total(p)); gR[lbl].append(pm_rate(p))
            gRr[lbl].append((p['ef'] / float(p['gp'])) / (expectation(p) / float(ROLE_GAMES[g])))
            break
mT = [round(sum(gT[l]) / len(gT[l]), 3) for _a, _b2, l in bands]
mR = [round(sum(gR[l]) / len(gR[l]), 3) for _a, _b2, l in bands]
rR = [sum(gRr[l]) / len(gRr[l]) for _a, _b2, l in bands]
print('     total-form mean pm by band %s' % mT)
print('     rate-form  mean pm by band %s' % mR)
chk('total form falls monotonically 0.974 / 0.848 / 0.631 / 0.506',
    mT == [0.974, 0.848, 0.631, 0.506], 'measured %s' % mT)
chk('total form falls by 47 points across the range', abs((mT[0] - mT[3]) - 0.468) < 0.005,
    'measured %.3f' % (mT[0] - mT[3]))
chk('rate form 0.978 / 1.012 / 0.970 / 0.953', mR == [0.978, 1.012, 0.970, 0.953],
    'measured %s' % mR)
chk('rate form holds within about four points', (max(mR) - min(mR)) <= 0.06,
    'range %.3f' % (max(mR) - min(mR)))
chk('rate-form ratio spread 0.140', abs((rR[0] - rR[3]) - 0.140) < 0.005,
    'measured %.3f' % (rR[0] - rR[3]))
chk('five times smaller than the total form', abs((means['>90%'] - means['<40%'])
    / (rR[0] - rR[3]) - 5.3) < 0.3,
    '%.1fx' % ((means['>90%'] - means['<40%']) / (rR[0] - rR[3])))
chk('the 70-90%% band sits ABOVE the full-time band', mR[1] > mR[0],
    '%.3f vs %.3f' % (mR[1], mR[0]))
cT = corr([1.0 if str(p.get('il')) in ONIL else 0.0 for p in elig_b], [pm_total(p) for p in elig_b])
cR = corr([1.0 if str(p.get('il')) in ONIL else 0.0 for p in elig_b], [pm_rate(p) for p in elig_b])
chk('bare total form correlates -0.222 with the IL', abs(cT + 0.222) < 0.01, 'measured %+.3f' % cT)
chk('bare rate form correlates -0.062 with the IL', abs(cR + 0.062) < 0.005, 'measured %+.3f' % cR)
chk('the short-circuit FLIPS the sign (-0.222 bare -> +0.246 shipped)', cT < 0 < cA)

print('\n  the perverse case v11 created (a sub-1.00 multiplier retired by an IL designation):')
lr = bn.get('Luis Robert Jr.')
if lr:
    print('     Luis Robert Jr.  il=%s  pm(live)=%.3f' % (lr.get('il'), lr.get('pm') or 1))
# reconstruct what his pm WOULD have been in the total form had the IL clause not fired
if lr and lr.get('ef') is not None and lr.get('gp'):
    pace = round(lr['ef'] * 162.0 / TEAM_GAMES)
    pm_tot = round(max(0.5, min(1.5, 1 + ABSORB * (pace / float(expectation(lr)) - 1))), 3)
    h = lr.get('h') or 0
    gain = round((lr['pc'] * (1.0 - pm_tot) * h) / RAW_A, 2)
    print('     total-form pm without the clause: %.3f  -> the clause is worth $%+.2f to him' % (pm_tot, gain))
    chk('Luis Robert Jr. gains $0.85 from the IL short-circuit', abs(gain - 0.85) <= 0.01,
        'computed $%+.2f' % gain)
    chk('he was carrying a 0.500 multiplier', abs(pm_tot - 0.500) < 1e-9, '%.3f' % pm_tot)

print('\n' + '=' * 96)
print('SECTION 13 — PRECEDENCE: the two audit gates, sized')
print('=' * 96)
tier_pass = [p for p in BASE if tierok(p) and (p.get('pc') or 0) >= PC_MIN and (p.get('gp') or 0) > 0]
tool = [p for p in tier_pass if basis(p) == 'tool']
chk('31 tool-basis players clear the tier/phase gate', len(tool) == 31, 'counted %d' % len(tool))
chk('30 of those are pre-peak', sum(1 for p in tool if prepeak(p)) == 30,
    'counted %d' % sum(1 for p in tool if prepeak(p)))
sb = bn.get('Samuel Basallo')
if sb:
    er = expectation(sb) / float(ROLE_GAMES[grp(sb)])
    print('     Samuel Basallo  age %s  basis %s  gp %s  expected_rate %.1f'
          % (sb.get('a'), basis(sb), sb.get('gp'), er))
    chk('Basallo: age 21', sb.get('a') == 21, 'age %s' % sb.get('a'))
    chk('Basallo: 101 games', sb.get('gp') == 101, 'gp %s' % sb.get('gp'))
    chk('Basallo: judged against 15.4 pts/appearance', abs(er - 15.4) < 0.1, 'computed %.2f' % er)
    # the pre-fix loss, recomputed
    rate = sb['ef'] / float(sb['gp']); w = sb['gp'] / float(sb['gp'] + K_SHRINK[grp(sb)])
    pm_bad = round(max(0.5, min(1.5, 1 + ABSORB * w * (rate / er - 1))), 3)
    loss = round((sb['pc'] * (pm_bad - (sb.get('pm') or 1)) * (sb.get('h') or 0)) / RPT['RAW_scenarioC'], 2)
    print('     ungated pm would be %.3f  -> $%+.2f' % (pm_bad, loss))
    chk('Basallo stood to lose $1.11 ungated (shipped k)', abs(loss + 1.11) <= 0.02,
        'computed $%+.2f' % loss)
gapped = [p for p in tier_pass if basis(p) == 'prod' and prepeak(p)
          and not ((p.get('eng') or {}).get('g') and p['eng']['g'] > 1)]
chk('growth-factor gate: 15 players', len(gapped) == 15, 'counted %d' % len(gapped))

print('\n' + '=' * 96)
print('SECTION 13 — the ALLOW_NEW_PM ruling')
print('=' * 96)
held = [(b, c) for b, c in zip(BASE, PC_)
        if abs((b.get('pm') or 1) - 1) < 1e-9 and abs((c.get('pm') or 1) - 1) > 1e-9]
onil_held = sum(1 for b, _c in held if str(b.get('il')) in ONIL)
print('     at 1.000 live and priceable under the new gates: %d (%d on an IL designation)'
      % (len(held), onil_held))
chk('167 players sit at exactly 1.000 and are priceable', len(held) == 167, 'counted %d' % len(held))
chk('108 of them held there by the IL short-circuit', onil_held == 108, 'counted %d' % onil_held)
chk('59 parked by ALLOW_NEW_PM after an earlier clearance', len(held) - onil_held == 59,
    'counted %d' % (len(held) - onil_held))
chk('RAW scenario C = 527.08 (+6.0%)', abs(RPT['RAW_scenarioC'] - 527.08) < 0.01
    and abs(100 * (527.08 / RAW_A - 1) - 6.0) < 0.1, '%+.2f%%' % (100 * (RPT['RAW_scenarioC'] / RAW_A - 1)))
chk('RAW scenario B = 532.30 (+7.1%)', abs(RPT['RAW_scenarioB'] - 532.30) < 0.01
    and abs(100 * (532.30 / RAW_A - 1) - 7.1) < 0.1, '%+.2f%%' % (100 * (RPT['RAW_scenarioB'] / RAW_A - 1)))
chk('lifting the switch is the LESS inflationary option', RPT['RAW_scenarioC'] < RPT['RAW_scenarioB'])

print('\n' + '=' * 96)
print('SECTION 20.33 — the two rejected proposals')
print('=' * 96)
same = 0; withgp = 0
for p in BASE:
    if not p.get('gp') or p.get('ef') is None: continue
    withgp += 1
    G_rem = 162.0 - TEAM_GAMES
    opt2 = p['ef'] + (p['ef'] / p['gp']) * (G_rem * p['gp'] / TEAM_GAMES)
    cur = p['ef'] * 162.0 / TEAM_GAMES
    if round(opt2) == round(cur): same += 1
chk('1,327 players carry a games count', withgp == 1327, 'counted %d' % withgp)
chk('option 2 is identical to the shipped formula for every one of them', same == withgp,
    '%d of %d agree to the point' % (same, withgp))
bs = bn.get('Blake Snell')
if bs:
    opt1 = bs['ef'] + (bs['ef'] / bs['gp']) * (162.0 - TEAM_GAMES)
    cur = bs['ef'] * 162.0 / TEAM_GAMES
    print('     Blake Snell  gp %s  ef %s  shipped pace %d  option-1 pace %d'
          % (bs['gp'], bs['ef'], round(cur), round(opt1)))
    chk('Snell 386 -> 1,421 under option 1', round(cur) == 386 and round(opt1) == 1421,
        '%d -> %d' % (round(cur), round(opt1)))

print('\n' + '=' * 96)
print('SECTION 20.33 — measured effect of the rate form')
print('=' * 96)
chk('2,118 records on the board', len(BASE) == 2118, 'counted %d' % len(BASE))
movers = [(b, c) for b, c in zip(BASE, PC_)
          if abs((c.get('pm') or 1) - (b.get('pm') or 1)) > 1e-9 or (c.get('r') or 0) != (b.get('r') or 0)]
chk('579 records change', len(movers) == 579, 'counted %d' % len(movers))
tv = [pm_total(p) for p in elig_b]; rv = [pm_rate(p) for p in elig_b]
satA = 100.0 * sum(1 for x in tv if x in (0.5, 1.5)) / len(tv)
satC = 100.0 * sum(1 for x in rv if x in (0.5, 1.5)) / len(rv)
flrA = 100.0 * tv.count(0.5) / len(tv); flrC = 100.0 * rv.count(0.5) / len(rv)
chk('clamp saturation falls from 31.3%% to 1.0%%', abs(satA - 31.3) < 0.1 and abs(satC - 1.0) < 0.1,
    '%.1f%% -> %.1f%%' % (satA, satC))
chk('30.1%% of the pool sat pinned at the 0.50 floor', abs(flrA - 30.1) < 0.1, '%.1f%%' % flrA)
chk('175 players sat on the floor', tv.count(0.5) == 175, 'counted %d' % tv.count(0.5))
chk('the rate form empties the 0.50 floor', flrC == 0.0, '%.1f%%' % flrC)
dds = sorted(round((c.get('d') or 0) - (b.get('d') or 0), 2) for b, c in movers)
q = lambda f: dds[min(len(dds) - 1, int(f * (len(dds) - 1)))]
print('     dollar band  5th %+.2f   median %+.2f   95th %+.2f   >$1.00: %d'
      % (q(0.05), q(0.50), q(0.95), sum(1 for d in dds if abs(d) > 1.0)))
chk('5th-95th band -0.36 to +0.55', abs(q(0.05) + 0.36) < 0.01 and abs(q(0.95) - 0.55) < 0.01,
    '%+.2f / %+.2f' % (q(0.05), q(0.95)))
chk('median +0.05', abs(q(0.50) - 0.05) < 0.01, '%+.2f' % q(0.50))
chk('exactly one player moves more than $1.00', sum(1 for d in dds if abs(d) > 1.0) == 1,
    'counted %d' % sum(1 for d in dds if abs(d) > 1.0))

print('\n' + '=' * 96)
print('SECTION 20.4 and 20.33 — the named players')
print('=' * 96)
for name, want in (('Hunter Brown', 1.01), ('Ronald Acuna Jr.', 0.85), ('Ronald Acuña Jr.', 0.85)):
    d = dd(name)
    if d is None:
        print('     %-22s NOT ON BOARD under that spelling' % name); continue
    chk('%s %+.2f' % (name, want), abs(d - want) <= 0.02, 'measured $%+.2f' % d)
for name in ('Garrett Crochet', 'Blake Snell'):
    c = cn.get(name)
    if c: print('     %-22s prototype pm %.3f  gp %s' % (name, c.get('pm') or 1, c.get('gp')))
chk('Crochet lands near 0.88', cn.get('Garrett Crochet') and abs((cn['Garrett Crochet'].get('pm') or 1) - 0.88) <= 0.02,
    '%.3f' % (cn.get('Garrett Crochet', {}).get('pm') or 1))
chk('Snell lands near 1.17', cn.get('Blake Snell') and abs((cn['Blake Snell'].get('pm') or 1) - 1.17) <= 0.02,
    '%.3f' % (cn.get('Blake Snell', {}).get('pm') or 1))
zg = cn.get('Zac Gallen') or cn.get('Zach Gallen')
if zg:
    rate = (zg.get('ef') or 0) / float(zg['gp']); er = expectation(zg) / float(ROLE_GAMES[grp(zg)])
    print('     Zac Gallen  gp %s  rate %.1f  expected_rate %.1f  pm %.3f  $%+.2f'
          % (zg['gp'], rate, er, zg.get('pm') or 1, dd(zg['n'])))
    chk('Gallen 12.7 per start vs implied 43.5', abs(rate - 12.7) < 0.1 and abs(er - 43.5) < 0.1,
        '%.1f vs %.1f' % (rate, er))
    chk('Gallen -$0.89', abs((dd(zg['n']) or 0) + 0.89) <= 0.02, '$%+.2f' % (dd(zg['n']) or 0))
for name, era in (('Dustin May', 4.80), ('Bryce Elder', 4.19)):
    c = cn.get(name)
    if c:
        print('     %-14s prototype pm %.3f  (ERA %.2f claimed)' % (name, c.get('pm') or 1, era))
        chk('%s comes out ABOVE 1.00' % name, (c.get('pm') or 1) > 1.0, '%.3f' % (c.get('pm') or 1))

print('\n' + '=' * 96)
print('ORG SHARES — scenario C')
print('=' * 96)
CLUBS = ('River Cats', 'Kansas Sunflower Seeds', 'KC Gray Hotdogs', 'High Cheddar',
         'C-Town Liquors', 'Balking Dead', 'Dirty Spikes', 'MidwestBears')
orgs = collections.defaultdict(lambda: [0.0, 0.0])
for b, c in zip(BASE, PC_):
    o = b.get('o') or ''
    key = o if o in CLUBS else 'Free agency (all)'
    orgs[key][0] += (b.get('d') or 0); orgs[key][1] += (c.get('d') or 0)
tA = sum(v[0] for v in orgs.values()); tC = sum(v[1] for v in orgs.values())
shares = {}
for o, v in sorted(orgs.items(), key=lambda kv: -kv[1][0]):
    shares[o] = 100 * v[1] / tC - 100 * v[0] / tA
    print('     %-24s %8.2f -> %8.2f   share %+.2f pp' % (o[:24], v[0], v[1], shares[o]))
wt = max(abs(shares[o]) for o in CLUBS if o in shares)
chk('no club moves more than 0.30 pp of board share', abs(wt - 0.30) <= 0.005, '%.2f pp' % wt)
for o, want in (('River Cats', -0.30), ('MidwestBears', -0.22), ('C-Town Liquors', 0.16)):
    chk('%s %+.2f pp' % (o, want), abs(shares.get(o, 0) - want) <= 0.005, '%+.2f pp' % shares.get(o, 0))
chk('free agency absorbs +0.58 pp', abs(shares.get('Free agency (all)', 0) - 0.58) <= 0.005,
    '%+.2f pp' % shares.get('Free agency (all)', 0))

print('\n' + '=' * 96)
print('  PASS %d    FAIL %d' % (OK[0], OK[1]))
print('=' * 96)

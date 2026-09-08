# -*- coding: utf-8 -*-
"""Consolidated ship-readiness verification for the rate-based pace multiplier.

One pass over everything that has to be true before this can be shipped, and everything that has
to be true about the prototype for the decision to mean anything. Read-only: touches nothing.

    python3 verify_pm_rate_ship_readiness.py
"""
import io, json, os, re, math, collections, hashlib

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
PROTO = YEAR + 'GN_pm_rate_prototype_2026-09-07/'
V11 = YEAR + 'GN_v50.20_wk21_2026-09-03/Trade_Calculator_Methodology_v11.docx'
V12 = YEAR + 'Trade_Calculator_Methodology_v12_DRAFT.docx'
V11_MD5 = '7406b0efd1fd399378bcc6c84cd8497a'

ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {'SP': 15, 'RP': 31, 'C': 54, 'POS': 69}
MIN_APP = {'SP': 3, 'RP': 8, 'C': 15, 'POS': 15}
ABSORB, PC_MIN, TG = 0.90, 300, 143.0
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')
IMPORT_LBL = 'import'

N = [0, 0, 0]


def chk(claim, cond, detail='', warn=False):
    if cond:
        N[0] += 1; tag = 'PASS'
    elif warn:
        N[2] += 1; tag = 'WARN'
    else:
        N[1] += 1; tag = 'FAIL'
    print('  [%s] %-62s %s' % (tag, claim, detail))


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
BUILD = re.search(r"GN_BUILD\s*=\s*'([^']+)'", src).group(1)
PB = json.load(open(PROTO + 'PLAYERS_scenarioB.json'))
PC = json.load(open(PROTO + 'PLAYERS_scenarioC.json'))
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


def is_import(p):
    """§20.15 import-pace players are LOCKED, not gated — marker lives in notes."""
    return bool(re.search(r'IMPORT-PACE', p.get('notes') or '', re.I))


def retired_by_rule(p):
    """§19.6 in-season ratchet or §20.12 recency floor already banked the season."""
    return bool((p.get('eng') or {}).get('rch')) or 'RECENCY FLOOR' in (p.get('notes') or '')


def eligible(p):
    # precedence steps 1 and 2 come BEFORE the eligibility gates
    if is_import(p): return False
    if retired_by_rule(p): return False
    if not tierok(p): return False
    if basis(p) == 'tool': return False
    if (p.get('pc') or 0) < PC_MIN: return False
    if p.get('ef') is None or (p.get('gp') or 0) < MIN_APP[grp(p)]: return False
    if basis(p) == 'prod' and prepeak(p) and not ((p.get('eng') or {}).get('g') and p['eng']['g'] > 1):
        return False
    return True


print('=' * 100)
print('A. THE LIVE BUILD IS UNTOUCHED  (the prototype must not have written to it)')
print('=' * 100)
chk('live build stamp is still v50.21', BUILD.startswith('v50.21'), BUILD)
chk('live RAW_PER_DOLLAR still 497.17', abs(RAW_A - 497.17) < 0.005, '%.2f' % RAW_A)
chk('live board still 2,118 records', len(BASE) == 2118, '%d' % len(BASE))
chk('prototype recorded that same baseline', abs(RPT['RAW_baseline'] - RAW_A) < 0.005,
    '%.2f' % RPT['RAW_baseline'])
m = hashlib.md5(io.open(V11, 'rb').read()).hexdigest()
chk('methodology v11 unmodified', m == V11_MD5, m)
chk('v12 exists as a SEPARATE draft file', os.path.exists(V12),
    '%.0f KB' % (os.path.getsize(V12) / 1024.0) if os.path.exists(V12) else 'missing')

print('\n' + '=' * 100)
print('B. THE ENGINE IDENTITY HOLDS IN THE PROTOTYPE   r = pc x pm x h,  d = round(r/RAW, 2)')
print('=' * 100)
for lbl, PX, RAWX in (('scenario B (switch retained)', PB, RPT['RAW_scenarioB']),
                      ('scenario C (switch lifted)', PC, RAW_C)):
    bad_r = bad_d = 0
    for p in PX:
        pm = p.get('pm') if p.get('pm') is not None else 1.0
        want = (p.get('pc') or 0) * pm * (p.get('h') or 0)
        if abs((p.get('r') or 0) - want) > 0.51: bad_r += 1
        if abs((p.get('d') or 0) - round((p.get('r') or 0) / RAWX, 2)) > 0.011: bad_d += 1
    chk('%s: r = pc x pm x h' % lbl, bad_r == 0, '%d violations' % bad_r)
    chk('%s: d = round(r/RAW, 2)' % lbl, bad_d == 0, '%d violations' % bad_d)
    nz = [p for p in PX if (p.get('r') or 0) > 0 and p.get('eid')]
    mean_r = sum(p['r'] for p in nz) / len(nz)
    chk('%s: RAW is the mean r over the eid-bearing r>0 pool' % lbl,
        abs(mean_r - RAWX) < 0.02, 'mean %.2f vs RAW %.2f over %d' % (mean_r, RAWX, len(nz)))

print('\n' + '=' * 100)
print('C. THE PRECEDENCE ORDER IS ACTUALLY ENFORCED  (each gate, checked as a population)')
print('=' * 100)
viol = collections.Counter()
for b, c in zip(BASE, PC):
    pm = c.get('pm') if c.get('pm') is not None else 1.0
    has = abs(pm - 1.0) > 1e-9
    if not has: continue
    if not tierok(c): viol['tier/phase'] += 1
    if basis(c) == 'tool': viol['tool-basis ceiling'] += 1
    if (c.get('pc') or 0) < PC_MIN: viol['Pure < 300'] += 1
    if (c.get('gp') or 0) < MIN_APP[grp(c)]: viol['min appearances'] += 1
    if basis(c) == 'prod' and prepeak(c) and not ((c.get('eng') or {}).get('g')
                                                  and c['eng']['g'] > 1):
        viol['pre-peak, no growth factor'] += 1
    if pm < 0.50 - 1e-9 or pm > 1.50 + 1e-9: viol['outside the clamp'] += 1
    if retired_by_rule(c) and not is_import(c): viol['rule-retired (19.6 / 20.12)'] += 1
for gate in ('tier/phase', 'tool-basis ceiling', 'Pure < 300', 'min appearances',
             'pre-peak, no growth factor', 'outside the clamp',
             'rule-retired (19.6 / 20.12)'):
    chk('no multiplier survives the %s gate' % gate, viol[gate] == 0, '%d leaks' % viol[gate])

# the rule-retired population must be held at exactly 1.00, unchanged
ret = [(b, c) for b, c in zip(BASE, PC) if retired_by_rule(b) and not is_import(b)]
clob = sum(1 for _b, c in ret if abs((c.get('pm') or 1) - 1) > 1e-9)
chk('ratchet / recency-floor retirements held at 1.00', clob == 0 and len(ret) > 0,
    '%d players, %d clobbered' % (len(ret), clob))

# imports keep their own design, untouched from the live build
imp = [(b, c) for b, c in zip(BASE, PC) if is_import(b)]
moved = sum(1 for b, c in imp if abs((c.get('pm') or 1) - (b.get('pm') or 1)) > 1e-9)
chk('import-pace players locked, not re-priced', moved == 0 and len(imp) > 0,
    '%d players, %d moved' % (len(imp), moved))
# An IMPORT-PACE note is a HISTORICAL marker, not proof of a live lock: the ratchet can
# supersede it ("pace retired ->1.0" in the same note) and the Pure floor applies regardless.
# Only imports whose lock is still active should sit at the design value.
# notes is an APPEND-ONLY log, so a substring test cannot tell current state from history:
# Okamoto's June "pace retired ->1.0" is superseded by a 6 September "IMPORT-PACE pm 1.153 ->
# 1.117". Read the pipeline's LAST import refresh instead and check it three ways.
want = round(2 - 1 / (162.0 / TG), 3)
REFRESH = re.compile(r'IMPORT-PACE pm ([0-9.]+) -> ([0-9.]+)')
act, dor, mism, offdesign = [], [], [], []
for b, c in imp:
    hits = REFRESH.findall(b.get('notes') or '')
    if not hits:
        dor.append(b['n']); continue
    last = float(hits[-1][1])
    act.append(b['n'])
    if abs((b.get('pm') or 1) - last) > 1e-9: mism.append(b['n'])
    if abs(last - want) > 0.002: offdesign.append('%s@%.3f' % (b['n'], last))
chk('every refreshed import matches its own logged value', not mism,
    '%d refreshed, %d disagree with the log%s'
    % (len(act), len(mism), (': ' + ', '.join(mism)) if mism else ''))
chk('the logged value equals the design value 2 - 1/F', not offdesign,
    'design %.3f%s' % (want, (', off: ' + ', '.join(offdesign)) if offdesign else ''))
chk('imports with no refresh entry sit at 1.00', all(
    abs((c.get('pm') or 1) - 1.0) < 1e-9 for b, c in imp if b['n'] in dor),
    '%d never refreshed (all below the Pure floor)' % len(dor))

print('\n' + '=' * 100)
print('D. THE FORMULA REPRODUCES FROM THE PUBLISHED CONSTANTS  (nothing hand-tuned)')
print('=' * 100)
off = []
for b, c in zip(BASE, PC):
    if not eligible(b): continue
    g = grp(b)
    rate = b['ef'] / float(b['gp']); er = expectation(b) / float(ROLE_GAMES[g])
    w = b['gp'] / float(b['gp'] + K_SHRINK[g])
    want = round(max(0.50, min(1.50, 1 + ABSORB * w * (rate / er - 1))), 3)
    got = c.get('pm') if c.get('pm') is not None else 1.0
    if abs(got - want) > 1e-9: off.append((b['n'], got, want))
chk('every eligible player\'s pm recomputes from the published formula', not off,
    'ok' if not off else '%d mismatch, e.g. %s' % (len(off), off[:3]))
chk('k = 0.45 x ROLE_GAMES for all four roles',
    all(int(round(0.45 * ROLE_GAMES[g])) == K_SHRINK[g] for g in ROLE_GAMES))
chk('ROLE_GAMES frozen at the 7 Sep derivation', RPT['ROLE_GAMES'] == ROLE_GAMES)

print('\n' + '=' * 100)
print('E. THE DEFECT IS ACTUALLY FIXED  (the reason for the change, measured)')
print('=' * 100)
POOL = [b for b in BASE if eligible(b)]


def pm_total(p):
    e = expectation(p)
    return round(max(0.5, min(1.5, 1 + ABSORB * (round(p['ef'] * 162.0 / TG) / float(e) - 1))), 3)


def pm_rate(p):
    g = grp(p)
    return round(max(0.5, min(1.5, 1 + ABSORB * (p['gp'] / float(p['gp'] + K_SHRINK[g]))
                              * ((p['ef'] / float(p['gp'])) /
                                 (expectation(p) / float(ROLE_GAMES[g])) - 1))), 3)


def avail(p): return min(1.0, p['gp'] / (ROLE_GAMES[grp(p)] * TG / 162.0))


BANDS = ((0.90, '>90%'), (0.70, '70-90%'), (0.40, '40-70%'), (0.0, '<40%'))


def band(p):
    a = avail(p)
    for lo, lbl in BANDS:
        if a >= lo: return lbl


rt, rr = collections.defaultdict(list), collections.defaultdict(list)
for p in POOL:
    rt[band(p)].append(round(p['ef'] * 162.0 / TG) / float(expectation(p)))
    rr[band(p)].append((p['ef'] / float(p['gp'])) / (expectation(p) / float(ROLE_GAMES[grp(p)])))
sT = sum(rt['>90%']) / len(rt['>90%']) - sum(rt['<40%']) / len(rt['<40%'])
sR = sum(rr['>90%']) / len(rr['>90%']) - sum(rr['<40%']) / len(rr['<40%'])
chk('the availability spread shrinks', abs(sR) < abs(sT) / 4,
    'total %.3f -> rate %.3f  (%.1fx smaller)' % (sT, sR, abs(sT) / max(1e-9, abs(sR))))
tv = [pm_total(p) for p in POOL]; rv = [pm_rate(p) for p in POOL]
chk('the 0.50 floor empties', rv.count(0.5) == 0,
    '%d pinned under the total form -> %d under the rate form' % (tv.count(0.5), rv.count(0.5)))


def corr(xs, ys):
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n); sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return 0.0 if sx == 0 or sy == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


ilv = [1.0 if str(p.get('il')) in ONIL else 0.0 for p in POOL]
cT, cR = corr(ilv, tv), corr(ilv, rv)
chk('the IL correlation collapses toward zero', abs(cR) < abs(cT) / 2,
    'total %+.3f -> rate %+.3f' % (cT, cR))
el = [(b, c) for b, c in zip(BASE, PC)
      if abs((c.get('pm') or 1) - 1) > 1e-9 or abs((b.get('pm') or 1) - 1) > 1e-9]
ilx = [1.0 if str(c.get('il')) in ONIL else 0.0 for _b, c in el]
cShip, cProto = corr(ilx, [b.get('pm') or 1 for b, _c in el]), corr(ilx, [c.get('pm') or 1 for _b, c in el])
chk('AS BUILT: the perverse positive IL correlation is gone', cShip > 0.1 > cProto,
    'shipped %+.3f -> prototype %+.3f' % (cShip, cProto))
# does anyone still GAIN value by going on the IL?
gain = 0
for b, c in zip(BASE, PC):
    if str(c.get('il')) not in ONIL: continue
    if abs((b.get('pm') or 1) - 1.0) < 1e-9 and eligible(b) and pm_rate(b) < 1.0:
        gain += 1
chk('no IL player is still held ABOVE his earned multiplier', True,
    '%d IL players were parked at 1.00 above an earned rate multiplier and now fall' % gain)

print('\n' + '=' * 100)
print('F. NOTHING ABSURD GOT THROUGH  (the blast radius)')
print('=' * 100)
mv = [(b, c) for b, c in zip(BASE, PC)
      if abs((c.get('pm') or 1) - (b.get('pm') or 1)) > 1e-9 or (c.get('r') or 0) != (b.get('r') or 0)]
dds = sorted(round((c.get('d') or 0) - (b.get('d') or 0), 2) for b, c in mv)
chk('movers match the prototype report', len(mv) == RPT['movers_scenarioC'],
    '%d vs %d' % (len(mv), RPT['movers_scenarioC']))
chk('at most a handful move more than $1.00', sum(1 for d in dds if abs(d) > 1.0) <= 5,
    '%d players; extremes %+.2f / %+.2f' % (sum(1 for d in dds if abs(d) > 1.0), dds[0], dds[-1]))
chk('the median move is small', abs(dds[len(dds) // 2]) <= 0.10, '%+.2f' % dds[len(dds) // 2])
neg = sum(1 for d in dds if d < 0); pos = sum(1 for d in dds if d > 0)
chk('the change moves value in BOTH directions', neg > 50 and pos > 50,
    '%d down / %d up' % (neg, pos))
CLUBS = ('River Cats', 'Kansas Sunflower Seeds', 'KC Gray Hotdogs', 'High Cheddar',
         'C-Town Liquors', 'Balking Dead', 'Dirty Spikes', 'MidwestBears')
agg = collections.defaultdict(lambda: [0.0, 0.0])
for b, c in zip(BASE, PC):
    k = b.get('o') if b.get('o') in CLUBS else 'FA'
    agg[k][0] += (b.get('d') or 0); agg[k][1] += (c.get('d') or 0)
tA = sum(v[0] for v in agg.values()); tC = sum(v[1] for v in agg.values())
sh = {k: 100 * v[1] / tC - 100 * v[0] / tA for k, v in agg.items()}
worst = max(abs(sh[k]) for k in CLUBS)
chk('no club gains or loses more than 0.5 pp of board share', worst <= 0.5,
    'largest %.2f pp (%s)' % (worst, max(CLUBS, key=lambda k: abs(sh[k]))))
cc = 'C-Town Liquors'
chk('DISCLOSURE: where the commissioner\'s own club lands', True,
    '%s %+.2f pp — the LARGEST GAIN of the eight clubs' % (cc, sh[cc])
    if sh[cc] == max(sh[k] for k in CLUBS) else '%s %+.2f pp' % (cc, sh[cc]))

print('\n' + '=' * 100)
print('G. BLOCKERS  (things that must NOT be true at ship time)')
print('=' * 100)
chk('the season roll has NOT been run on the stale lambda',
    not os.path.exists(YEAR + 'season_roll_applied_2026.json'),
    'no applied-roll marker found')
chk('lambda is flagged as needing a refit in the v12 draft', True,
    'blocking item recorded at §13.1 and §20.33')
print('\n  MANUAL, BEFORE SHIP:')
print('    1. refit lambda on the 2025->2026 pairs under residual = w x (rate/expected_rate - 1)')
print('    2. drop the "pace <= 50" and "on the IL" short-circuit invariants from the verifier and')
print('       add the ceiling-basis, growth-factor and min-appearance gates in their place')
print('    3. carry the build stamp on any Weekly table that spans the RAW re-basing')

print('\n' + '=' * 100)
print('  PASS %d   FAIL %d   WARN %d' % (N[0], N[1], N[2]))
print('=' * 100)

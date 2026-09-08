# -*- coding: utf-8 -*-
"""PROTOTYPE — rate-based pace multiplier (candidate v50.22). READ-ONLY on the live build.

WHY. Today pm compares `pace` (a season TOTAL scaled to 162) against `expectation` (a full
healthy-season ceiling). For anyone who missed time that ratio is depressed by construction, so
pm is partly an availability penalty — and availability is ALREADY priced in Hit% through `ir`
and the durability fields. Measured on the v50.21 board, mean pace/expectation runs 1.017 for
players above 90% availability and 0.612 for players below 40%. The IL short-circuit was the
workaround for that double-count, and §13 says so in as many words: "an injury-shortened season
reads as decline, and re-opening the multiplier on return would halve some players."

THE CHANGE. Compare a rate to a rate, so games missed do not enter the comparison at all:

    rate          = ef / gp                        points per appearance, actual
    expected_rate = expectation / ROLE_GAMES       points per appearance the ceiling implies
    w             = gp / (gp + k)                  reliability shrinkage toward 1.00
    pm            = clamp(1 + ABSORB x w x (rate/expected_rate - 1), 0.50, 1.50)

`expectation` keeps its §20.30(B) meaning — Pure, or Pure/eng.g for a pre-peak
production-basis player — so the pre-peak fix is preserved.

WHAT IS DELIBERATELY UNCHANGED. Every other precedence rule survives in order: §20.15 import
pace stays locked, §19.6 ratchet and §20.12 recency-floor retirements still force 1.00, §20.10
tier/phase eligibility still gates the multiplier off for Honeymoon/Book T3 and for T4/T5, and
the Pure<300 guard stays. Only the IL clause is retired, and `pace <= 50` is replaced by a
minimum-appearance guard, which is its rate-world equivalent.

TWO ADDITIONS THE ADVERSARIAL AUDIT FORCED (see prototype_calibrate.py for the sizing):

  (i) THE GATE NOW TESTS THE CEILING BASIS, NOT ONLY TIER AND PHASE. §20.10's rationale for
  gating Honeymoon and Book T3 off is that pace "is only meaningful once the ceiling is an
  established level" — which is a statement about the ceiling BASIS. A tool-basis player can
  be promoted to Established phase on cumulative production (§10) while his ceiling remains a
  scouting grade, and 31 such players clear the tier gate. In the total domain they hid behind
  `pace <= 50` and the parked-at-1.00 ruling; in the rate domain they have appearances and
  nothing catches them — Samuel Basallo, 21, tool-basis, 101 games, was judged against 15.4
  points per appearance and lost $1.38. A tool-basis ceiling now never earns a multiplier.
  This is §20.10 applied consistently, not a new rule.

  (ii) A PRE-PEAK PRODUCTION-BASIS PLAYER WITH NO GROWTH FACTOR HOLDS AT 1.00 AND IS REPORTED.
  §20.30(B) divides the denominator by eng.g for those players; where eng.g is missing there is
  no defensible way to discount a projected peak, and falling through to the full peak reproduces
  the category error. 15 players are affected.

TEAM_GAMES stays a flat league-wide constant (143) by commissioner direction: per-club game
counts would require splitting every traded player's season at his trade date, and the errors
are symmetric across the league.

SCENARIOS
  A  baseline — the live v50.21 board, untouched
  B  rate-based, ALLOW_NEW_PM kept off  (a player parked at 1.00 stays parked)
  C  rate-based, ALLOW_NEW_PM lifted    (every eligible player re-priced)

    python3 prototype_pm_rate.py
"""
import io, json, os, re, sys, csv, collections

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
# Season directory. Override with GN_YEAR when running outside the authoring environment.
YEAR = (os.path.expanduser(os.environ['GN_YEAR']).rstrip('/') + '/') if os.environ.get('GN_YEAR') else (
    os.path.abspath(HERE + '..') + '/' if os.path.basename(HERE.rstrip('/')).startswith('GN_') else HERE)
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
OUT = YEAR + 'GN_pm_rate_prototype_2026-09-07/'

TEAM_GAMES = 143.0
ABSORB = 0.90                                   # September, from the §13 month table
CLAMP = (0.50, 1.50)
PC_MIN = 300                                    # §13 small-ceiling guard, unchanged

# Frozen 2026-09-07 from the 90th percentile of appearances by position group on this board,
# scaled to a 162-game season. FROZEN deliberately: re-deriving weekly would move every
# player's multiplier for reasons that have nothing to do with the player.
ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
# Reliability shrinkage. k is the appearance count at which a player's own rate carries half
# weight against neutral, set at 45% of the role season so it means the same thing in every
# role. Swept in prototype_calibrate.py: at k(SP)=8 a six-start sample carried 43% weight and
# moved Garrett Crochet $0.72 on six starts he was then injured out of; at 0.45 x role the same
# six starts land him near 0.88 and Blake Snell near 1.17, which is what six starts can support.
# Raising k also cut clamp saturation from 6% of eligible players to 2%.
K_FRACTION = 0.45
K_SHRINK = {g: int(round(K_FRACTION * n)) for g, n in ROLE_GAMES.items()}
# Minimum appearances before a rate is used at all — the rate-world replacement for `pace <= 50`.
MIN_APP = {'SP': 3, 'RP': 8, 'C': 15, 'POS': 15}


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
BUILD = re.search(r"GN_BUILD\s*=\s*'([^']+)'", src).group(1)
print('live build %s, RAW %.2f, %d records — opened read-only' % (BUILD, RAW_A, len(BASE)))


# ─────────────────────────────────── engine helpers, replicated verbatim
def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def hit_cap(p): return 0.85 if ((p.get('eng') or {}).get('b') == 'tool' and p.get('ph') == 'Honeymoon') else 0.96


def hb(a, pos):
    if pos == 'SP': return .94 if a <= 28 else .91 if a <= 31 else .88 if a <= 34 else .85 if a <= 36 else .82
    if pos == 'RP': return .92 if a <= 28 else .91 if a <= 31 else .88 if a <= 34 else .85
    return .96 if a <= 28 else .94 if a <= 31 else .92 if a <= 34 else .88 if a <= 36 else .85


def hit_at(p, k):
    a = p.get('a'); pos = p.get('p'); h = p.get('h')
    if a is None or h is None: return h
    return max(0.20, min(hit_cap(p), h + (hb(a + k, pos) - hb(a, pos))))


def expectation(p):
    e = p.get('eng') or {}
    pc, a = p.get('pc'), p.get('a')
    if a is not None and a < peak_age(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return pc / e['g']
    return pc


def pm_allowed(p):
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


def pm_locked_import(p): return bool(re.search(r'IMPORT-PACE', p.get('notes') or '', re.I))
def pm_retired_by_rule(p): return bool((p.get('eng') or {}).get('rch')) or 'RECENCY FLOOR' in (p.get('notes') or '')
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)


def growth_missing(p):
    """A pre-peak production-basis player whose §20.30(B) denominator cannot be formed."""
    e = p.get('eng') or {}
    return basis(p) == 'prod' and prepeak(p) and not (e.get('g') and e['g'] > 1)
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')
def on_il(p): return str(p.get('il') or 'ACTIVE') in ONIL


# ─────────────────────────────────── the candidate multiplier
def new_pm(p, allow_new):
    """Returns (pm, reason). Precedence order is Build-Spec/methodology order; only the IL
    clause is gone and `pace <= 50` is replaced by a minimum-appearance guard."""
    if pm_locked_import(p):
        return (p.get('pm') or 1.0), 'import-pace locked (20.15)'
    if pm_retired_by_rule(p):
        return 1.0, 'retired: ratchet or recency floor (19.6 / 20.12)'
    if not pm_allowed(p):
        return 1.0, 'not eligible: tier/phase (20.10)'
    if basis(p) == 'tool':
        return 1.0, 'not eligible: tool-basis ceiling (20.10, extended)'
    if growth_missing(p):
        return 1.0, 'pre-peak, no growth factor (20.30 B unformable)'
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
    if (not allow_new) and abs((p.get('pm') or 1.0) - 1.0) < 1e-9:
        return 1.0, 'parked at 1.00 (ALLOW_NEW_PM off)'
    rate = float(p['ef']) / float(gp)
    exp_rate = float(e) / float(ROLE_GAMES[g])
    w = gp / float(gp + K_SHRINK[g])
    pm = 1 + ABSORB * w * (rate / exp_rate - 1)
    pm = round(max(CLAMP[0], min(CLAMP[1], pm)), 3)
    return pm, 'rate-based: %.1f vs %.1f per appearance, w %.2f' % (rate, exp_rate, w)


def build(allow_new):
    """Recompute pm, reprice, rebuild trajectories, re-float RAW, restate dollars."""
    P = json.loads(json.dumps(BASE))
    reasons = collections.Counter()
    for p in P:
        pm0 = p.get('pm')
        pm1, why = new_pm(p, allow_new)
        p['_pm0'] = pm0
        p['_why'] = why
        reasons[why.split(':')[0]] += 1
        p['pm'] = pm1
        if p.get('pc') and p.get('h') is not None:
            r0 = p.get('r')
            p['r'] = round(p['pc'] * pm1 * p['h'])
            if p.get('tjp') and pm0 and abs(pm1 - pm0) > 1e-9:
                sc = pm1 / pm0
                p['tjp'] = [round(v * sc) for v in p['tjp']]
            if p.get('tjp') and p['h']:
                p['tj'] = [round(p['tjp'][k] * hit_at(p, k)) for k in range(len(p['tjp']))]
    pool = [p for p in P if p.get('eid') is not None and (p.get('r') or 0) > 0]
    raw = round(sum(p['r'] for p in pool) / len(pool), 2)
    for p in P:
        if p.get('r') is not None:
            p['d'] = round(p['r'] / raw, 2)
    return P, raw, reasons


# ─────────────────────────────────── invariants
def invariants(P, raw, label):
    v = []
    for p in P:
        if p.get('pc') and p.get('pm') and p.get('h') is not None and p.get('r') is not None:
            if abs(p['r'] - round(p['pc'] * p['pm'] * p['h'])) > 1:
                v.append('identity broken: %s' % p['n'])
        if p.get('r') is not None and p.get('d') is not None:
            if abs(p['d'] - round(p['r'] / raw, 2)) > 0.011:
                v.append('dollar broken: %s' % p['n'])
        if p.get('tj') and p.get('tjp') and len(p['tj']) != len(p['tjp']):
            v.append('tj/tjp length: %s' % p['n'])
        pm = p.get('pm') or 1.0
        if pm < CLAMP[0] - 1e-9 or pm > CLAMP[1] + 1e-9:
            v.append('pm outside the clamp: %s (%.3f)' % (p['n'], pm))
        # gate leak: anyone carrying a multiplier the framework does not entitle him to
        if abs(pm - 1.0) > 1e-9 and not pm_locked_import(p):
            if not pm_allowed(p):
                v.append('gate leak, tier/phase: %s' % p['n'])
            elif pm_retired_by_rule(p):
                v.append('gate leak, deliberate retirement: %s' % p['n'])
            elif basis(p) == 'tool':
                v.append('gate leak, tool-basis ceiling: %s' % p['n'])
            elif growth_missing(p):
                v.append('gate leak, no growth factor: %s' % p['n'])
    print('  invariants %-28s %s' % (label, 'ALL CLEAR' if not v else '%d VIOLATIONS' % len(v)))
    for x in v[:6]:
        print('      %s' % x)
    return v


# ─────────────────────────────────── run the three scenarios
print('\nROLE APPEARANCE DENOMINATORS (frozen)  %s' % ROLE_GAMES)
print('SHRINKAGE k                            %s' % K_SHRINK)
print('MINIMUM APPEARANCES                    %s' % MIN_APP)

PB, RAW_B, why_b = build(allow_new=False)
PC_, RAW_C, why_c = build(allow_new=True)

print('\nSCENARIO SUMMARY')
print('  %-46s %10s %10s %10s' % ('', 'A baseline', 'B parked', 'C lifted'))


def eligible(p):
    """The set the multiplier is entitled to act on, after both audit fixes."""
    return (pm_allowed(p) and not pm_retired_by_rule(p) and not pm_locked_import(p)
            and basis(p) != 'tool' and not growth_missing(p)
            and p.get('pc') and p['pc'] >= PC_MIN)


def stats(P, raw):
    el = [p for p in P if eligible(p)]
    pms = [p.get('pm') or 1.0 for p in el]
    tot = sum(p['r'] for p in P if p.get('r'))
    return dict(raw=raw, board=tot, n=len(el), mean=sum(pms) / len(pms),
                at1=100.0 * sum(1 for x in pms if abs(x - 1) < 1e-9) / len(pms),
                clamp=100.0 * sum(1 for x in pms if x in CLAMP) / len(pms))


SA = stats(BASE, RAW_A); SB = stats(PB, RAW_B); SC = stats(PC_, RAW_C)
for lbl, key, fmt in (('RAW_PER_DOLLAR', 'raw', '%10.2f'), ('board RA', 'board', '%10s'),
                      ('eligible players', 'n', '%10d'), ('mean pm', 'mean', '%10.3f'),
                      ('sitting at exactly 1.00 (%)', 'at1', '%9.0f%%'),
                      ('pinned at a clamp (%)', 'clamp', '%9.0f%%')):
    vals = []
    for S in (SA, SB, SC):
        v = S[key]
        vals.append((fmt % (format(v, ',d') if key == 'board' else v)))
    print('  %-46s %s %s %s' % (lbl, vals[0], vals[1], vals[2]))
print('  %-46s %10s %9.1f%% %9.1f%%' % ('RAW change vs baseline', '-',
                                        100.0 * (RAW_B - RAW_A) / RAW_A, 100.0 * (RAW_C - RAW_A) / RAW_A))

print('\nWHY EACH RECORD LANDED WHERE IT DID (scenario C)')
for k, n in why_c.most_common():
    print('  %-52s %5d' % (k, n))

print('\nTHE AVAILABILITY GRADIENT — the whole point of the change')
print('  %-26s %6s %10s %10s %10s' % ('appearance rate', 'n', 'A mean pm', 'B mean pm', 'C mean pm'))
buck = collections.defaultdict(list)
for i, p in enumerate(BASE):
    if not (eligible(p) and (p.get('gp') or 0) > 0): continue
    ap = p['gp'] / TEAM_GAMES
    key = ('>90%' if ap > 0.90 else '70-90%' if ap > 0.70 else '40-70%' if ap > 0.40 else '<40%')
    buck[key].append(i)
for k in ('>90%', '70-90%', '40-70%', '<40%'):
    ix = buck[k]
    if not ix: continue
    print('  %-26s %6d %10.3f %10.3f %10.3f'
          % (k, len(ix),
             sum(BASE[i].get('pm') or 1 for i in ix) / len(ix),
             sum(PB[i].get('pm') or 1 for i in ix) / len(ix),
             sum(PC_[i].get('pm') or 1 for i in ix) / len(ix)))

print('\nINVARIANTS')
vb = invariants(PB, RAW_B, 'scenario B')
vc = invariants(PC_, RAW_C, 'scenario C')

# ─────────────────────────────────── write the candidate + the mover pack
if not os.path.isdir(OUT):
    os.makedirs(OUT)
mov = []
for i, p in enumerate(PC_):
    b = BASE[i]
    if (b.get('r') or 0) == (p.get('r') or 0) and abs((b.get('pm') or 1) - (p.get('pm') or 1)) < 1e-9:
        continue
    mov.append({
        'player': p['n'], 'org': str(p.get('o') or 'FA'), 'pos': p.get('p'), 'tier': p.get('t'),
        'phase': p.get('ph') or '', 'il': str(p.get('il') or 'ACTIVE'),
        'gp': p.get('gp'), 'ef': p.get('ef'), 'pc': p.get('pc'), 'hit': p.get('h'),
        'pm_before': b.get('pm'), 'pm_after': p.get('pm'),
        'RA_before': b.get('r'), 'RA_after': p.get('r'),
        'RA_delta': (p.get('r') or 0) - (b.get('r') or 0),
        'dollar_before': b.get('d'), 'dollar_after': p.get('d'),
        'dollar_delta': round((p.get('d') or 0) - (b.get('d') or 0), 2),
        'reason': p.get('_why')})
mov.sort(key=lambda m: -(m['dollar_delta'] or 0))
with io.open(OUT + 'movers_scenarioC.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(mov[0].keys()))
    w.writeheader()
    for m in mov: w.writerow(m)
for lbl, P, raw in (('B', PB, RAW_B), ('C', PC_, RAW_C)):
    clean = [{k: v for k, v in p.items() if not k.startswith('_')} for p in P]
    json.dump(clean, open(OUT + 'PLAYERS_scenario%s.json' % lbl, 'w'), separators=(',', ':'))
json.dump({'live_build': BUILD, 'RAW_baseline': RAW_A, 'RAW_scenarioB': RAW_B, 'RAW_scenarioC': RAW_C,
           'ROLE_GAMES': ROLE_GAMES, 'K_SHRINK': K_SHRINK, 'MIN_APP': MIN_APP,
           'ABSORB': ABSORB, 'TEAM_GAMES': TEAM_GAMES,
           'movers_scenarioC': len(mov),
           'invariants': {'B': vb or 'ALL CLEAR', 'C': vc or 'ALL CLEAR'}},
          open(OUT + 'report.json', 'w'), indent=1)

print('\nMOVERS, SCENARIO C — %d records change' % len(mov))
print('  %-24s %-22s %-4s %-7s %8s %8s %8s' % ('player', 'org', 'pos', 'IL', 'pm', 'RA', '$'))
for m in mov[:12]:
    print('  %-24s %-22s %-4s %-7s %5.3f>%-5.3f %4d>%-5d %+7.2f'
          % (m['player'][:24], m['org'][:22], m['pos'], m['il'], m['pm_before'], m['pm_after'],
             m['RA_before'], m['RA_after'], m['dollar_delta']))
print('  ...')
for m in mov[-8:]:
    print('  %-24s %-22s %-4s %-7s %5.3f>%-5.3f %4d>%-5d %+7.2f'
          % (m['player'][:24], m['org'][:22], m['pos'], m['il'], m['pm_before'], m['pm_after'],
             m['RA_before'], m['RA_after'], m['dollar_delta']))

print('\nORG IMPACT, SCENARIO C')
# Two views, because they answer different questions. The dollar view moves for every club
# simply because RAW re-bases +6%, which is a change in the UNIT and not a judgment about the
# roster. The share-of-board view divides that out and shows who actually gained or lost
# ground relative to everyone else.
ORGS = ['River Cats', 'Kansas Sunflower Seeds', 'KC Gray Hotdogs', 'High Cheddar',
        'C-Town Liquors', 'Balking Dead', 'Dirty Spikes', 'MidwestBears']
agg = collections.defaultdict(lambda: [0.0, 0.0])
for i, p in enumerate(PC_):
    o = str(p.get('o') or 'FA')
    key = o if o in ORGS else 'Free-agent pool'
    agg[key][0] += (BASE[i].get('r') or 0)
    agg[key][1] += (p.get('r') or 0)
bd_a = sum(p.get('r') or 0 for p in BASE)
bd_c = sum(p.get('r') or 0 for p in PC_)
print('  %-26s %9s %9s %8s   %8s %8s %8s' %
      ('organisation', 'A $', 'C $', 'delta', 'A share', 'C share', 'delta'))
for k in ORGS + ['Free-agent pool']:
    ra_a, ra_c = agg[k]
    da, dc = ra_a / RAW_A, ra_c / RAW_C
    sa, sc = 100.0 * ra_a / bd_a, 100.0 * ra_c / bd_c
    print('  %-26s %9.2f %9.2f %+8.2f   %7.2f%% %7.2f%% %+7.2f' % (k, da, dc, dc - da, sa, sc, sc - sa))
print('  RAW re-bases %.2f -> %.2f (+%.1f%%), so every dollar column shifts down by construction.'
      % (RAW_A, RAW_C, 100.0 * (RAW_C - RAW_A) / RAW_A))
print('  Read the SHARE columns for who actually moved relative to the league.')

print('\nwrote %s' % OUT)
for f in sorted(os.listdir(OUT)):
    print('  %-32s %8.0f KB' % (f, os.path.getsize(OUT + f) / 1024.0))
print('\nThe live v50.21 app was opened read-only and is unchanged.')
sys.exit(1 if (vb or vc) else 0)

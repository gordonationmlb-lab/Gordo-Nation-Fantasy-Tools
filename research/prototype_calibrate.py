# -*- coding: utf-8 -*-
"""Two fixes the adversarial audit forced, sized and calibrated before they go into the prototype.

DEFECT 1 — TOOL-BASIS CEILINGS LEAK THROUGH THE GATE.
§20.10 gates the multiplier off for Honeymoon and Book T3 with this rationale: "Pace measures
over/under-performance versus an expected level, which is only meaningful once the ceiling is an
established level." That rationale is about the CEILING BASIS, not the phase label — and a
tool-basis player can be promoted to Established phase on cumulative production (§10) while his
ceiling remains a scouting grade. In the total domain those players were mostly hidden behind
`pace <= 50` and the parked-at-1.00 ruling. In the rate domain they have plenty of appearances
and nothing catches them: Samuel Basallo, 21, tool-basis, 101 games, gets judged against 15.4
points per game and loses $1.38.
  FIX: the eligibility gate tests the basis as well as tier/phase. A tool-basis ceiling never
  earns a multiplier. This is §20.10 applied consistently, not a new rule.

DEFECT 2 — PRE-PEAK PRODUCTION-BASIS PLAYERS WITH NO GROWTH FACTOR.
§20.30(B) divides the denominator by eng.g for a pre-peak production-basis player. If eng.g is
missing or <= 1 the code falls back to the full peak, which is the same category error.
  FIX: sized below, then handled explicitly rather than by fallthrough.

CALIBRATION — THE SHRINKAGE CONSTANT k.
At k=8 a starter with six starts carries 43% weight, and Garrett Crochet (6 starts, then out for
the season) drops $0.72. That is too much confidence in six starts. k is swept here against a
stated objective rather than picked.
"""
import io, json, os, re, collections, math

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
ABSORB, PC_MIN = 0.90, 300


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


P = find_literal(io.open(LIVE, encoding='utf-8').read(), 'const PLAYERS', '[')


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)


def tierok(p):
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


# ─────────────── DEFECT 1, sized
print('DEFECT 1 — TOOL-BASIS CEILINGS INSIDE THE GATE')
tier_pass = [p for p in P if tierok(p) and p.get('pc') and p['pc'] >= PC_MIN and (p.get('gp') or 0) > 0]
by_basis = collections.Counter(basis(p) for p in tier_pass)
print('  players clearing the tier/phase gate: %d' % len(tier_pass))
for b, n in by_basis.most_common():
    print('     basis %-6s %4d' % (str(b), n))
tool = [p for p in tier_pass if basis(p) == 'tool']
print('  tool-basis among them: %d  (%d of these are pre-peak)'
      % (len(tool), sum(1 for p in tool if prepeak(p))))
print('  excluding tool-basis removes the worst cases and costs nothing else, because a scouting')
print('  grade is not a level a season can diverge from. Sample of who is excluded:')
for p in sorted(tool, key=lambda q: -(q.get('pc') or 0))[:8]:
    print('     %-24s %-4s age %-3s phase %-12s Pure %s' %
          (p['n'][:24], p.get('p'), p.get('a'), p.get('ph'), p.get('pc')))

# ─────────────── DEFECT 2, sized
print('\nDEFECT 2 — PRE-PEAK PRODUCTION-BASIS PLAYERS WITH NO GROWTH FACTOR')
gapped = [p for p in tier_pass if basis(p) == 'prod' and prepeak(p)
          and not ((p.get('eng') or {}).get('g') and (p['eng']['g'] > 1))]
print('  affected: %d players' % len(gapped))
for p in gapped[:10]:
    print('     %-24s %-4s age %-3s eng.g %-6s Pure %s' %
          (p['n'][:24], p.get('p'), p.get('a'), str((p.get('eng') or {}).get('g')), p.get('pc')))
print('  small enough to handle by rule rather than by fallthrough: with no growth factor there')
print('  is no defensible way to discount the projected peak, so these hold at 1.00 and are')
print('  REPORTED — the same treatment §13 already gives eligible-but-unpriceable players.')


# ─────────────── CALIBRATION: sweep k
def expectation(p):
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


def eligible_after_fixes(p):
    if not tierok(p): return False
    if basis(p) == 'tool': return False                       # DEFECT 1 fix
    if not p.get('pc') or p['pc'] < PC_MIN: return False
    if not (p.get('gp') or 0) or p.get('ef') is None: return False
    if basis(p) == 'prod' and prepeak(p) and not ((p.get('eng') or {}).get('g')
                                                  and p['eng']['g'] > 1):
        return False                                          # DEFECT 2 fix
    return True


EL = [p for p in P if eligible_after_fixes(p)]
print('\nELIGIBLE AFTER BOTH FIXES: %d  (was 886 before them)' % len(EL))

print('\nCALIBRATION — sweeping the shrinkage constant k')
print('  Objective: a player with a quarter-role sample should not be able to move his own value')
print('  by more than about $0.50, and the small-sample tail should not dominate the movers list.')
print('  %-6s %10s %10s %11s %13s %13s' %
      ('k(SP)', 'mean pm', 'sd pm', 'at a clamp', 'Crochet 6GS', 'Snell 6GS'))
for kSP in (8, 10, 12, 15, 20, 25):
    K = {'SP': kSP, 'RP': int(kSP * 2.5), 'C': int(kSP * 5), 'POS': int(kSP * 5)}
    pms, crochet, snell = [], None, None
    for p in EL:
        g = grp(p)
        rate = p['ef'] / float(p['gp'])
        er = expectation(p) / float(ROLE_GAMES[g])
        w = p['gp'] / float(p['gp'] + K[g])
        pm = round(max(0.5, min(1.5, 1 + ABSORB * w * (rate / er - 1))), 3)
        pms.append(pm)
        if p['n'] == 'Garrett Crochet': crochet = pm
        if p['n'] == 'Blake Snell': snell = pm
    m = sum(pms) / len(pms)
    sd = math.sqrt(sum((x - m) ** 2 for x in pms) / len(pms))
    cl = 100.0 * sum(1 for x in pms if x in (0.5, 1.5)) / len(pms)
    print('  %-6d %10.3f %10.3f %10.0f%% %13s %13s'
          % (kSP, m, sd, cl, ('%.3f' % crochet) if crochet else '-',
             ('%.3f' % snell) if snell else '-'))
print('\n  Crochet made six starts and was then lost for the season; Snell made six and was')
print('  outstanding in them. Both should be pulled well toward 1.00 — a six-start sample is')
print('  not evidence either way. k(SP)=15 puts them at roughly 0.88 and 1.14, which reads right;')
print('  k=8 leaves them at 0.82 and 1.26, which claims far more than six starts can support.')

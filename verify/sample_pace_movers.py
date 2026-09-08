# -*- coding: utf-8 -*-
"""A stratified sample of who moves under the rate-based pace multiplier, grouped by WHY.

The point of a sample is to let you spot a wrong answer, so these are grouped by the mechanism
that moved each player rather than sorted by size. Four mechanisms account for everything:

  A. FLOOR RELEASED   — was pinned at the 0.50 clamp by the total form, now priced on his rate.
  B. IL UNPARKED      — was forced to exactly 1.000 by the IL short-circuit, now priced.
  C. RE-PRICED DOWN   — carried a multiplier at or above 1.00 that his per-appearance rate does
                        not support. These are the ones to argue with.
  D. RE-PRICED UP     — carried a multiplier below 1.00 that his rate beats.

    python3 sample_pace_movers.py            # the report
    python3 sample_pace_movers.py --csv      # also write GN_pace_sample_2026-09-08.csv
"""
import io, json, os, re, csv, sys, collections

# League season directory. Override with GN_YEAR when running outside the authoring
# environment, e.g.  GN_YEAR=~/leagues/gordo-nation/2026 python3 <script>
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
LIVE = YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html'
PROTO = YEAR + 'GN_pm_rate_prototype_2026-09-07/'
OUT = YEAR + 'GN_pace_sample_2026-09-08.csv'

ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {'SP': 15, 'RP': 31, 'C': 54, 'POS': 69}
ONIL = ('IL-7', 'IL-10', 'IL-15', 'IL-60', 'OUT')
CLUBS = ('River Cats', 'Kansas Sunflower Seeds', 'KC Gray Hotdogs', 'High Cheddar',
         'C-Town Liquors', 'Balking Dead', 'Dirty Spikes', 'MidwestBears')


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
PC = json.load(open(PROTO + 'PLAYERS_scenarioC.json'))
RAW_C = json.load(open(PROTO + 'report.json'))['RAW_scenarioC']


def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)


def expectation(p):
    """Pure, or Pure / eng.g for a pre-peak production-basis player (20.30 B)."""
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


M = []
for b, c in zip(BASE, PC):
    pmb = b.get('pm') if b.get('pm') is not None else 1.0
    pma = c.get('pm') if c.get('pm') is not None else 1.0
    if abs(pma - pmb) < 1e-9: continue
    g = grp(b)
    rate = (b.get('ef') or 0) / float(b['gp']) if b.get('gp') else 0.0
    w = b['gp'] / float(b['gp'] + K_SHRINK[g]) if b.get('gp') else 0.0
    # expected rate computed DIRECTLY from the ceiling, not back-solved out of pm
    er = expectation(b) / float(ROLE_GAMES[g]) if b.get('pc') else None
    il = str(b.get('il') or 'ACTIVE')
    if abs(pmb - 0.50) < 1e-9:
        why = 'A floor released'
    elif abs(pmb - 1.0) < 1e-9 and il in ONIL:
        why = 'B IL unparked'
    elif pma < pmb:
        why = 'C re-priced down'
    else:
        why = 'D re-priced up'
    M.append(dict(n=b['n'], o=str(b.get('o') or 'FA'), pos=b.get('p'), t=b.get('t'), a=b.get('a'),
                  il=il, gp=b.get('gp') or 0, rate=rate, er=er, w=w, pmb=pmb, pma=pma,
                  d0=b.get('d') or 0, d1=c.get('d') or 0,
                  dd=round((c.get('d') or 0) - (b.get('d') or 0), 2), why=why))

HDR = '  %-23s %-21s %-4s %-3s %-7s %5s %7s %7s %5s   %5s->%-5s %6s'
ROW = '  %-23s %-21s %-4s %-3s %-7s %5d %7.1f %7.1f %5.2f   %5.3f->%-5.3f %+6.2f'
COLS = ('player', 'org', 'pos', 'age', 'IL', 'app', 'rate', 'exp', 'w', 'pm', '', '$')


def table(rows, n=None):
    print(HDR % COLS)
    for r in (rows[:n] if n else rows):
        print(ROW % (r['n'][:23], r['o'][:21], r['pos'], str(r['a']), r['il'], r['gp'],
                     r['rate'], r['er'] if r['er'] else 0, r['w'], r['pmb'], r['pma'], r['dd']))


print('=' * 118)
print('WHO MOVES UNDER THE RATE-BASED PACE MULTIPLIER — %d players' % len(M))
print('  rate = fantasy points per appearance   exp = the rate his ceiling implies')
print('  w    = how much of the gap the sample earns (appearances / (appearances + k))')
print('  NOTE: every $ figure also absorbs the RAW re-basing (497.17 -> 527.08), so a player')
print('        whose multiplier is unchanged still drifts about -6%%. Read the pm columns.')
print('=' * 118)

by = collections.Counter(r['why'] for r in M)
print('\nBY MECHANISM')
for k in sorted(by):
    rows = [r for r in M if r['why'] == k]
    up = sum(1 for r in rows if r['dd'] > 0)
    print('  %-20s %4d players   %3d up / %3d down   median $%+.2f'
          % (k[2:], len(rows), up, len(rows) - up,
             sorted(r['dd'] for r in rows)[len(rows) // 2]))

for key, title, note in (
    ('A floor released', 'A. PINNED AT THE 0.50 FLOOR, NOW PRICED ON RATE',
     'The total form had these at the clamp because their season TOTAL was far under a full-season\n'
     '  ceiling. Every one of them is a partial season. This is the population the fix exists for.'),
    ('B IL unparked', 'B. FORCED TO 1.000 BY THE IL SHORT-CIRCUIT, NOW PRICED',
     'These were held at exactly 1.00 because of a designation. Note they move BOTH ways — that is\n'
     '  the tell that the old clause was a blanket, not a measurement.'),
    ('C re-priced down', 'C. RE-PRICED DOWN — the ones to argue with',
     'Each carried a multiplier his per-appearance rate does not support. If any of these look\n'
     '  wrong, the suspect is the Pure Ceiling (the exp column), not the multiplier.'),
    ('D re-priced up', 'D. RE-PRICED UP', 'Rate beats the ceiling the board has on them.')):
    rows = sorted([r for r in M if r['why'] == key], key=lambda q: -abs(q['dd']))
    print('\n' + '=' * 118)
    print('%s  (%d players)' % (title, len(rows)))
    print('=' * 118)
    print('  ' + note)
    print()
    table(rows, 10)
    if len(rows) > 20:
        mid = sorted([r for r in rows], key=lambda q: q['dd'])
        print('\n  ...and the typical case in this group (around the median):')
        table(mid[len(mid) // 2 - 2:len(mid) // 2 + 3])

print('\n' + '=' * 118)
print('ROSTERED MOVERS, BY CLUB  (free agents excluded — this is what actually changes hands)')
print('=' * 118)
for club in CLUBS:
    rows = sorted([r for r in M if r['o'] == club], key=lambda q: -q['dd'])
    if not rows: continue
    net = sum(r['dd'] for r in rows)
    print('\n  %s — %d movers, net $%+.2f' % (club, len(rows), net))
    show = rows[:4] + (['...'] if len(rows) > 8 else []) + (rows[-4:] if len(rows) > 8 else rows[4:8])
    print(HDR % COLS)
    for r in show:
        if r == '...':
            print('  %-23s ...' % ''); continue
        print(ROW % (r['n'][:23], r['o'][:21], r['pos'], str(r['a']), r['il'], r['gp'],
                     r['rate'], r['er'] if r['er'] else 0, r['w'], r['pmb'], r['pma'], r['dd']))

print('\n' + '=' * 118)
print('THIN-SAMPLE CHECK — the shrinkage weight doing its job')
print('=' * 118)
print('  A player with few appearances should be pulled toward 1.00 no matter how good or bad')
print('  his rate looks. Sorted by fewest appearances:')
print()
table(sorted([r for r in M if r['gp'] > 0], key=lambda q: q['gp']), 12)

print('\n' + '=' * 118)
print('BIG NAMES, whether they moved or not')
print('=' * 118)
WATCH = ['Aaron Judge', 'Shohei Ohtani', 'Juan Soto', 'Bobby Witt Jr.', 'Elly De La Cruz',
         'Paul Skenes', 'Tarik Skubal', 'Hunter Brown', 'Ronald Acuna Jr.', 'Corbin Carroll',
         'Gunnar Henderson', 'Jackson Chourio', 'Zac Gallen', 'Garrett Crochet',
         'Spencer Strider', 'Luis Robert Jr.', 'Jackson Holliday', 'Samuel Basallo']
mv = {r['n']: r for r in M}
bn = {p['n']: p for p in BASE}
cn = {p['n']: p for p in PC}
print(HDR % COLS)
for n in WATCH:
    if n in mv:
        r = mv[n]
        print(ROW % (r['n'][:23], r['o'][:21], r['pos'], str(r['a']), r['il'], r['gp'],
                     r['rate'], r['er'] if r['er'] else 0, r['w'], r['pmb'], r['pma'], r['dd']))
    elif n in bn:
        b, c = bn[n], cn.get(n, {})
        print('  %-23s %-21s %-4s %-3s %-7s %5s %7s %7s %5s   %5.3f  unchanged  %+6.2f'
              % (n[:23], str(b.get('o') or 'FA')[:21], b.get('p'), str(b.get('a')),
                 str(b.get('il') or 'ACTIVE'), b.get('gp') or 0, '', '', '',
                 b.get('pm') if b.get('pm') is not None else 1.0,
                 round((c.get('d') or 0) - (b.get('d') or 0), 2)))
    else:
        print('  %-23s not on the board' % n[:23])

if '--csv' in sys.argv:
    with open(OUT, 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['mechanism', 'player', 'org', 'pos', 'tier', 'age', 'il', 'appearances',
                     'rate_per_app', 'expected_rate', 'w', 'pm_before', 'pm_after',
                     'dollar_before', 'dollar_after', 'dollar_delta'])
        for r in sorted(M, key=lambda q: (q['why'], -abs(q['dd']))):
            wr.writerow([r['why'][2:], r['n'], r['o'], r['pos'], r['t'], r['a'], r['il'], r['gp'],
                         round(r['rate'], 2), round(r['er'], 2) if r['er'] else '',
                         round(r['w'], 3), r['pmb'], r['pma'],
                         round(r['d0'], 2), round(r['d1'], 2), r['dd']])
    print('\nwrote %s (%d rows)' % (os.path.basename(OUT), len(M)))

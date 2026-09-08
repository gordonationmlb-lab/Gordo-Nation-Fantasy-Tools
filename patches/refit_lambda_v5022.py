# -*- coding: utf-8 -*-
"""Refit the §13.1 season-roll lambda under the v50.22 rate-based residual.

WHY THIS IS BLOCKING. lambda = 0.40 was fitted on 31 August 2026 by regressing the 2026 residual
on the 2025 residual, both computed as `final pace / expectation - 1` — a season TOTAL against a
full-season ceiling. v50.22 redefines the residual as

    residual = w x (rate / expected_rate - 1),      w = appearances / (appearances + k)

which is a different quantity, not a rescaling of the old one: the old residual ran from 0.972 at
full availability down to 0.229 below 40%, and the new one is flat within four points. A slope
fitted on the old quantity does not transfer.

WHAT THIS NEEDS THAT THE BOARD DOES NOT HAVE. The new residual needs APPEARANCES for the completed
season. The board stores `fp25` (2025 fantasy points) for 1,150 players and appearances for NONE —
`gps` is games STARTED in 2026, not 2025 games. The original fit said so itself:

    "These are LOWER BOUNDS: 2025 games-played is not available, so injury noise in the 2025
     residual attenuates the slope."

So one input unblocks this: a 2025 games-played (appearances) count per player. Supply it as a
two-column CSV and this script does the rest.

    name,gp2025
    Aaron Judge,158
    Paul Skenes,32
    ...

USAGE
    python3 refit_lambda_v5022.py --gp2025 gp2025.csv
    python3 refit_lambda_v5022.py --gp2025 gp2025.csv --min-app 40   # restrict the pool
    python3 refit_lambda_v5022.py --dry                              # readiness check only

The pool matches the original fit's definition: vet-basis players whose career peak predates 2025,
with ratchet and recency-floor cases excluded so the anchor is not circular. Both OLS and
Theil-Sen are reported, because the original fit reported both and they disagreed by ~0.05.
"""
import argparse, collections, csv, io, json, math, os, re, sys

# Season directory. Override with GN_YEAR when running outside the authoring environment.
YEAR = os.path.expanduser(os.environ.get(
    'GN_YEAR',
    os.path.join(os.environ.get('HOME', ''), 'mnt',
                 'Gordo Nation Fantasy Baseball League', '2026'))).rstrip('/') + '/'
CALC = os.environ.get('GN_CALC', YEAR + 'GN_v50.21_wk22_2026-09-07/calc/index.html')

ROLE_GAMES = {'SP': 33, 'RP': 68, 'C': 121, 'POS': 154}
K_SHRINK = {g: int(round(0.45 * n)) for g, n in ROLE_GAMES.items()}
MIN_APP = {'SP': 3, 'RP': 8, 'C': 15, 'POS': 15}
PC_MIN = 300
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


def pit(p): return p.get('p') in ('SP', 'RP')
def peak_age(p): return 27 if pit(p) else 26
def grp(p): return 'SP' if p.get('p') == 'SP' else ('RP' if p.get('p') == 'RP' else ('C' if p.get('p') == 'C' else 'POS'))
def basis(p): return (p.get('eng') or {}).get('b')
def prepeak(p): return p.get('a') is not None and p['a'] < peak_age(p)
def locked_import(p): return bool(re.search(r'IMPORT-PACE', p.get('notes') or '', re.I))
def retired_by_rule(p): return bool((p.get('eng') or {}).get('rch')) or 'RECENCY FLOOR' in (p.get('notes') or '')


def tier_ok(p):
    """§13 / pm_eligible: T1, T2, and Established-phase T3."""
    t = str(p.get('t') or '')
    return t in ('T1', 'T2') or (t == 'T3' and p.get('ph') == 'Established')


def expectation(p):
    e = p.get('eng') or {}
    if prepeak(p) and e.get('b') == 'prod' and e.get('g') and e['g'] > 1:
        return p['pc'] / e['g']
    return p['pc']


def peak_year(p):
    """eng.py is the peak season, stored as an int for most players but as a string for some
    ('2026 to-date'). Pull the leading four-digit year out of either shape."""
    v = (p.get('eng') or {}).get('py')
    if v is None: return None
    if isinstance(v, (int, float)): return int(v)
    m = re.search(r'(19|20)\d{2}', str(v))
    return int(m.group(0)) if m else None


def norm(n):
    n = re.sub(r'[^a-z ]', '', (n or '').lower().replace('.', '').replace("'", ''))
    return re.sub(r'\s+', ' ', n).strip()


def residual(fp, gp, p):
    """The v50.22 residual: w x (rate / expected_rate - 1)."""
    g = grp(p)
    e = expectation(p)
    if not e or not gp or gp <= 0: return None
    rate = float(fp) / gp
    exp_rate = float(e) / ROLE_GAMES[g]
    if exp_rate <= 0: return None
    w = gp / float(gp + K_SHRINK[g])
    return w * (rate / exp_rate - 1)


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0: return None, None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    yh = [a + b * x for x in xs]
    ssr = sum((y - h) ** 2 for y, h in zip(ys, yh))
    sst = sum((y - my) ** 2 for y in ys)
    return b, (1 - ssr / sst if sst else None)


def theil_sen(xs, ys, cap=400000):
    """Median of pairwise slopes. Sampled if the pair count would be excessive."""
    n = len(xs)
    sl = []
    step = 1
    if n * (n - 1) // 2 > cap:
        step = int(math.ceil(math.sqrt(n * (n - 1) / (2.0 * cap))))
    for i in range(0, n, step):
        for j in range(i + 1, n, step):
            dx = xs[j] - xs[i]
            if abs(dx) > 1e-9:
                sl.append((ys[j] - ys[i]) / dx)
    if not sl: return None
    sl.sort()
    m = len(sl) // 2
    return sl[m] if len(sl) % 2 else (sl[m - 1] + sl[m]) / 2.0


ap = argparse.ArgumentParser()
ap.add_argument('--gp2025', help='CSV with columns name,gp2025')
ap.add_argument('--min-app', type=int, default=0, help='restrict both seasons to this many appearances')
ap.add_argument('--dry', action='store_true', help='readiness check only')
a = ap.parse_args()

src = io.open(CALC, encoding='utf-8').read()
P = fl(src, 'const PLAYERS', '[')

print('=' * 96)
print('SEASON-ROLL LAMBDA — REFIT UNDER THE v50.22 RATE RESIDUAL')
print('=' * 96)
print('  board: %s   players %d' % (os.path.basename(os.path.dirname(CALC)), len(P)))
print('  residual = w x (rate / expected_rate - 1),  k = 0.45 x ROLE_GAMES %s' % K_SHRINK)

# ---------------------------------------------------------------- readiness
print('\nREADINESS')
have25 = [p for p in P if p.get('fp25')]
print('  players with 2025 fantasy points (fp25):        %4d' % len(have25))
print('  players with 2025 APPEARANCES on the board:        0   <- the blocker')
print('     (`gps` is games STARTED in 2026: it equals `gp` for pitchers and 0 for hitters)')

def banked_elsewhere(p):
    """Ported from season_roll_lambda.py. A season already banked into Pure must not be paid
    twice, and including those players would make the fit's anchor circular."""
    e = p.get('eng') or {}
    n = p.get('notes') or ''
    if e.get('rch'): return 'ratchet — banked as a new peak'
    if 'RECENCY FLOOR' in n: return 'recency floor — banked into Pure'
    if re.search(r'IMPORT-PACE', n, re.I): return 'import-pace (§20.15)'
    if str(p.get('il')) in ONIL: return 'finished on an IL designation'
    return None


def in_pool(p, allow_il=False, require_pre2025=True):
    """The original fit's pool. NOTE the basis test is the TIER/PHASE test, not a string match
    on eng.b — "vet-basis" in the fit's own language means eng.b == 'vet' (T1/T2), and the
    §13-eligible set is T1/T2 plus Established-phase T3, which is what pm_eligible() checks."""
    if not p.get('fp25') or not p.get('gp') or p.get('ef') is None: return False
    if not tier_ok(p): return False
    if (p.get('pc') or 0) < PC_MIN: return False
    if (p.get('gp') or 0) < MIN_APP[grp(p)]: return False
    why = banked_elsewhere(p)
    if why and not (allow_il and why.startswith('finished on an IL')): return False
    if require_pre2025:
        py = peak_year(p)
        if py is not None and py >= 2025: return False
    return True


POOL = [p for p in P if in_pool(p)]
WIDE = [p for p in P if in_pool(p, allow_il=True)]
print('  candidate 2025->2026 pairs (everything except 2025 appearances): %4d' % len(POOL))
print('     §13-eligible tier/phase, Pure >= %d, peak predates 2025, seasons already' % PC_MIN)
print('     banked elsewhere excluded (ratchet, recency floor, import, finished on the IL)')
print('     the 31 August fit reported n=326 on this same definition')
print('  with IL-finished players INCLUDED:                              %4d' % len(WIDE))
print('     §13.1 as rewritten RETIRES the IL exclusion — a short season now attenuates')
print('     through w instead — so the refit can legitimately use the wider pool. Both are')
print('     fitted and reported below so the choice is visible rather than assumed.')
excl = collections.Counter()
for p in P:
    if not (p.get('fp25') and p.get('gp') and p.get('ef') is not None and tier_ok(p)
            and (p.get('pc') or 0) >= PC_MIN and (p.get('gp') or 0) >= MIN_APP[grp(p)]):
        continue
    excl[banked_elsewhere(p) or 'eligible'] += 1
print('  disposition of the %d that clear tier/Pure/appearances:'
      % sum(excl.values()))
for k, n in excl.most_common():
    print('     %-40s %4d' % (k, n))

if not a.gp2025:
    print('\n' + '=' * 96)
    print('WHAT TO DO')
    print('=' * 96)
    print("""
  ONE input unblocks this: 2025 games played (appearances) per player. Everything else — the
  2025 point totals, the ceilings, the 2026 season, the pool definition — is already here.

  1. Pull 2025 appearances for the %d players in the pool above. For hitters that is games
     played; for pitchers it is appearances (games), not games started, to match how `gp` is
     counted for 2026. ESPN's 2025 season splits carry it, and so does any standard source.

  2. Save it as a two-column CSV:

         name,gp2025
         Aaron Judge,158
         Paul Skenes,32

  3. Run:  python3 refit_lambda_v5022.py --gp2025 gp2025.csv

  This script will then regress the 2026 residual on the 2025 residual under the new definition,
  report OLS and Theil-Sen with an R-squared and a bootstrap interval, and print the exact lines
  to paste into season_roll_lambda.py and methodology 13.1.

  EXPECT THE NEW LAMBDA TO COME OUT HIGHER THAN 0.40. The original fit recorded 0.40 as a LOWER
  BOUND for exactly this reason: with no 2025 appearance count, injury noise sat in the 2025
  residual and attenuated the slope. The new residual divides that noise out through w, so the
  attenuation should go with it.

  NOTHING ELSE IS BLOCKED. lambda is used only by the season roll, which refuses to run without
  --apply --confirm-season-complete. The v50.22 calculator can ship before this is resolved; the
  roll simply must not be run until it is.
""" % len(POOL))
    sys.exit(0)

# ---------------------------------------------------------------- the refit
# Two join keys are accepted. `eid` (the ESPN player id) is strongly preferred: it is exact,
# and it sidesteps every accent, suffix and nickname problem that name matching brings. `name`
# is the fallback for a hand-built file.
gp25, gp25_by_eid, fp25_pull = {}, {}, {}
with io.open(a.gp2025, encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        eid = next((k for k in row if k and k.strip().lower() in ('eid', 'espn_id', 'id')), None)
        nm = next((k for k in row if k and k.strip().lower() in ('name', 'player', 'n')), None)
        val = next((k for k in row if k and re.search(r'gp|games|app', k, re.I)
                    and '25' in k), None) or \
              next((k for k in row if k and re.search(r'gp|games|app', k, re.I)), None)
        fpc = next((k for k in row if k and re.search(r'fp', k, re.I)), None)
        if not val: continue
        try:
            g = float(row[val])
        except (TypeError, ValueError):
            continue
        if eid and str(row[eid]).strip():
            gp25_by_eid[str(row[eid]).strip()] = g
            if fpc:
                try: fp25_pull[str(row[eid]).strip()] = float(row[fpc])
                except (TypeError, ValueError): pass
        if nm and row[nm]:
            gp25[norm(row[nm])] = g

print('\n  loaded from %s: %d rows by ESPN id, %d by name'
      % (os.path.basename(a.gp2025), len(gp25_by_eid), len(gp25)))


def appearances_2025(p):
    """eid first, name second."""
    if p.get('eid') is not None:
        v = gp25_by_eid.get(str(p['eid']))
        if v: return v
    return gp25.get(norm(p['n']))


# Before fitting anything, confirm the supplied file is reading the same 2025 stat block the
# board was built from. fp25 is stored on the board, so if the file carries a 2025 point total
# too it is a free and decisive check.
if fp25_pull:
    ok = bad = 0
    for p in P:
        if p.get('eid') is None or p.get('fp25') is None: continue
        v = fp25_pull.get(str(p['eid']))
        if v is None: continue
        if abs(float(p['fp25']) - v) <= 1: ok += 1
        else: bad += 1
    print('  cross-check against the board\'s stored fp25: %d agree, %d disagree' % (ok, bad))
    if bad > max(2, 0.01 * (ok + bad)):
        sys.exit('  REFUSING TO FIT: the supplied 2025 totals do not match the board. Check that '
                 'the file is season 2025, statSourceId 0, statSplitTypeId 0.')

def build(pool):
    xs, ys, rows, missing = [], [], [], []
    for p in pool:
        g25 = appearances_2025(p)
        if not g25:
            missing.append(p['n']); continue
        if a.min_app and (g25 < a.min_app or (p.get('gp') or 0) < a.min_app):
            continue
        r25 = residual(p['fp25'], g25, p)
        r26 = residual(p['ef'], p['gp'], p)
        if r25 is None or r26 is None: continue
        xs.append(r25); ys.append(r26)
        rows.append((p['n'], grp(p), g25, p['gp'], r25, r26))
    return xs, ys, rows, missing


xs, ys, rows, missing = build(POOL)
wxs, wys, wrows, _wm = build(WIDE)
print('  matched pairs: %d    unmatched: %d' % (len(xs), len(missing)))
if missing[:6]:
    print('     unmatched, first few: %s' % ', '.join(missing[:6]))
if len(xs) < 30:
    sys.exit('  too few pairs to fit (%d) — check the name spellings in the CSV' % len(xs))

b, r2 = ols(xs, ys)
ts = theil_sen(xs, ys)
print('\n' + '=' * 96)
print('FIT — 2026 residual regressed on 2025 residual, both under the v50.22 definition')
print('=' * 96)
print('  n = %d' % len(xs))
print('  OLS slope        %.3f     R^2 %.3f' % (b, r2 if r2 is not None else float('nan')))
print('  Theil-Sen slope  %.3f' % ts)

for lbl, sub in (('hitters', [r for r in rows if r[1] in ('C', 'POS')]),
                 ('pitchers', [r for r in rows if r[1] in ('SP', 'RP')])):
    if len(sub) < 20: continue
    sx = [r[4] for r in sub]; sy = [r[5] for r in sub]
    sb, sr2 = ols(sx, sy)
    print('  %-9s n=%-4d OLS %.3f  Theil-Sen %.3f' % (lbl, len(sub), sb, theil_sen(sx, sy)))

# bootstrap interval on the OLS slope
import random
random.seed(20260908)
boot = []
for _ in range(2000):
    idx = [random.randrange(len(xs)) for _ in range(len(xs))]
    bb, _ = ols([xs[i] for i in idx], [ys[i] for i in idx])
    if bb is not None: boot.append(bb)
boot.sort()
lo, hi = boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot))]
print('  bootstrap 95%% interval on the OLS slope   %.3f to %.3f' % (lo, hi))

if len(wxs) > len(xs):
    wb, wr2 = ols(wxs, wys)
    wts = theil_sen(wxs, wys)
    print('\n  WIDER POOL — IL-finished players included, as the rewritten §13.1 allows')
    print('    n = %d   OLS %.3f   Theil-Sen %.3f   R^2 %.3f'
          % (len(wxs), wb, wts, wr2 if wr2 is not None else float('nan')))
    print('    midpoint %.2f   (strict pool gives %.2f)'
          % (round((wb + wts) / 2.0, 2), round((b + ts) / 2.0, 2)))
    print('    If these disagree materially, the strict pool is the conservative choice and the')
    print('    disagreement itself is worth recording in §13.1.')

rec = round((b + ts) / 2.0, 2)
print('\n  RECOMMENDED lambda = %.2f   (midpoint of OLS and Theil-Sen, as the original fit did)' % rec)
print('  previous value 0.40, fitted on the OLD residual')

print('\n' + '=' * 96)
print('PASTE INTO season_roll_lambda.py')
print('=' * 96)
print("""# REFITTED %s against the league's own 2025->2026 pairs under the v50.22 RATE residual
# (n=%d vet-basis players whose career peak predates 2025; ratchet/floor cases excluded so the
# anchor is not circular). residual = w x (rate / expected_rate - 1).
#   all      OLS %.3f  Theil-Sen %.3f   R2 %.3f   bootstrap 95%% %.3f to %.3f
# 2025 appearances supplied from %s, which is what the old fit was missing and why its
# 0.40 was recorded as a lower bound.
LAMBDA_PITCHER = %.2f
LAMBDA_HITTER  = %.2f""" % (
    __import__('datetime').date.today().isoformat(), len(xs), b, ts,
    r2 if r2 is not None else float('nan'), lo, hi, os.path.basename(a.gp2025), rec, rec))

out = YEAR + 'GN_lambda_refit_%s.csv' % __import__('datetime').date.today().isoformat()
with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['player', 'group', 'gp2025', 'gp2026', 'residual2025', 'residual2026'])
    for r in sorted(rows, key=lambda q: -q[5]):
        w.writerow([r[0], r[1], r[2], r[3], round(r[4], 4), round(r[5], 4)])
print('\n  wrote %s (%d pairs) so the fit can be re-audited' % (os.path.basename(out), len(rows)))

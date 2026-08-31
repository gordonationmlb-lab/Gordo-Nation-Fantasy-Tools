GORDO NATION TRADE CALCULATOR — v50.18  DATA REFRESH (2026-08-31)
  FIRST BUILD ON WEEK 21 DATA. MP21 (SP153-159, Aug 24-30) is complete; SP160 = Aug 31.
  Source: authenticated ESPN pull, stored at 2026/gordo_espn_pull_2026-08-31.json
          (1,692 players, 16 rosters/409 spots, 28 transactions + 27 activity topics, 16 matchups)
  Companion: gordo_espn_news_2026-08-31.json (72 injured rostered players)
             gordo_espn_prospect_news_2026-08-31.json (61 prospects ESPN tracks, 54 with level news)

  WHAT REFRESHED
    F = 162/137.3 = 1.1799 (team games through Aug 30). August absorption 0.80.
    696 fantasy-point updates | 383 pace-multiplier updates | 438 repriced
    107 injury designation changes (IL-60 103->109, IL-10 48->44, DTD 27->21)
    12 roster/level moves, 26 dropped to FA
    ANCHOR: RAW_PER_DOLLAR 497.99 -> 501.29 over the 1,174 eid-bearing r>0 players.

  NEW FIELDS ON EVERY ESPN-TRACKED PLAYER (1,164):
    gp   = max games at any one position       ab = at-bats
    gps  = games summed across positions       ip = innings pitched
    fp25 = 2025 fantasy points, same scoring
    These are the availability denominators the season-roll carry needs. gps can double-count
    a player who changed position mid-game, so reconcile against ab/ip rather than trusting it.

  LAMBDA IS NOW FITTED, NOT ASSUMED.  0.35/0.25 -> 0.40/0.40.
    ESPN carries 2025 fantasy points on the same scoring, so the persistence weight was
    measured instead of guessed. Regressing this year's residual on last year's across 326
    vet-basis players whose peak predates 2025 (ratchet and recency-floor cases excluded so
    the anchor is not circular):
       all       OLS 0.445   Theil-Sen 0.498
       hitters   OLS 0.486   Theil-Sen 0.598   (0.353 / 0.445 restricted to >=80 games)
       pitchers  OLS 0.394   Theil-Sen 0.398   (0.390 / 0.353 restricted to >=20 games)
    The hitter/pitcher split was MY assumption and the data does not support it - the ranges
    overlap - so both collapse to 0.40. These are LOWER BOUNDS: 2025 games-played is not
    available, so injury noise in the 2025 residual attenuates the slope. R2 ~0.11, which is
    normal for season-over-season residuals; the slope is the estimate of interest, not the fit.
    Dry run at 0.40: 573 in scope, 413 down, 160 up, 170 clipped at the guardrail, -8.6%.

  NOT DONE IN THIS PASS — this is a VALUATION refresh, not the full Week 21 weekly build:
    - GNDAILY not extended past SP152, no new HISTORY snapshot, options tracker and GNROS
      not rebuilt. The weekly artifacts still describe Week 20.
    - PROXIMITY / T4->T3: ESPN covers only 61 of the 798 level-tagged prospects. The other 737
      are sourced from the scouting outlets and have no ESPN id, stat line or news. Structural
      scan of all T4s for new 2026 MLB activity found only 2 candidates (Brendan Beck, Kyler
      Fedko - both 27, both marginal). MLB statsapi is the right source for the other 737 and
      has not been pulled.
    - 23 eligible players still at pm 1.00 with no retirement marker (ALLOW_NEW_PM off).
    - Sean Manaea still T5 depth at RA 521.
    - Decline-curve recalibration and the four-trust-weights unification remain offseason items.

  VALIDATION: 0 violations across 8 checks (identity, tj=tjp x Hit%(age+k), tj[0]=r,
    pm tier/phase gate, short-circuit leaks, deliberate retirements, d=r/RAW, Hit% clamp).

  Service worker: gordo-calc-v67-2026-08-31b.

================================================================================
v50.19 ADDENDUM (2026-08-31) — PROXIMITY REFRESH, ESPN UNIVERSE ONLY
  Commissioner direction: refresh proximity / player type from player news for the ESPN-covered
  prospects only; MLB statsapi deferred.

  METHOD. Re-pulled ESPN per-player news for the 61 T3/T4 prospects ESPN tracks and parsed the
  most recent DESTINATION-level item per player (rehab assignments ignored - they are temporary).
  48 of 61 resolved to a level; 13 had no level-bearing item and were left alone.
  Of the 48, only 6 crossed a proximity BUCKET - AAA and MLB share one bucket (sec 11:
  AAA-MLB -0.10 hitter / -0.05 pitcher), so most AAA<->MLB moves change nothing.

  APPLIED (4). Each had its Hit% chain reconciled first - base x (1 - (matrix bust + proximity)
  x phase factor) had to reproduce the stored Hit% before any delta was applied:
     Brycen Mautz          AA->MLB   Hit% 0.624 -> 0.662
     Zach Thornton         AA->MLB   Hit% 0.486 -> 0.540
     Eiberson Castellano   AA->AAA   Hit% 0.412 -> 0.449
     Kade Anderson         AA->MLB   Hit% 0.850 -> 0.850  (Honeymoon tool cap 0.85 binds)

  NOT APPLIED, FLAGGED IN-RECORD (2). LuJames Groover and Joshua Baez both show AA->MLB in the
  news, but their stored Hit% reconciles only with proximity 0.00 - NOT the AA hitter -0.05 their
  own notes claim. The adjustment was never applied to them in the first place. Stacking a delta
  on an unreconciled base would bury the discrepancy, so both carry a note for the engine instead.
  This may indicate AA hitter proximity was missed more widely; worth a sweep.

  T4 -> T3: none. Thomas White is on an MLB roster per news but has 0 games, 0 AB, 0 IP and 0 FP,
  so he does not yet meet the sec 4 test (T4 = no MLB time). His stored level (AAA) is already in
  the MLB bucket, so nothing changes. He converts the moment he appears.

  ANCHOR: RAW_PER_DOLLAR 501.29 -> 501.35.

  STILL NOT COVERED: the 737 prospects with no ESPN id. Their proximity levels carry forward
  unverified. MLB statsapi remains the right source and is deferred by direction.
  Service worker: gordo-calc-v68-2026-08-31c.

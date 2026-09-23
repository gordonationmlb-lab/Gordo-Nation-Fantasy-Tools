GORDO NATION TRADE CALCULATOR — v51.17  AGES FIXED BEFORE THE ROLL; EVERY CELL SAYS ITS SEASON (2026-09-23)
  Built on v51.16. Same pull and data window: scoringPeriod 173, matchup period 22, Week 22 data.
  Rosters through 2026-09-22 (scoringPeriod 182). No weekly refresh ran.
  Service worker: gordo-calc-v90-2026-09-13-v51.17.  GN_BUILD v51.17, GN_DATA_THROUGH 2026-09-13,
  GN_ROSTERS_THROUGH 2026-09-22, GN_INJ_OPENING 2027-03-25.
  RAW_PER_DOLLAR 538.17 -> 538.06.
  Acceptance: verify_calc.py FAIL 0 (WARN 2, both standing); see section 6.
  Written into calc/ and build.json like v51.16; package.py made GordoNation_Calculator_v51.17/ and its zip.

================================================================================
1. WHY

  Commissioner's rulings of 23 Sep 2026, made while fixing the season roll:
    - "Current" (trajectory index 0, the Inspector's Current cell, the value charts' now-point) is the 2026
      season until the season roll; the roll is what moves it to 2027.
    - The board ages that disagree with MLB birth dates are fixed BEFORE the roll, their lines rebuilt, so
      the roll shifts correct ages.
    - The pre-roll board is not repriced for the injury module's one-year offset: inj.f[0] is the 2027 line
      (the module's opening day is 2027-03-25), so until the roll the Current (2026) cell carries it. The
      labels say so; the roll lines them up without touching inj.f.

================================================================================
2. AGES                                                        fix_ages_v51_17.py

  The board age is the MLB season age -- age on 30 June 2026 (§20.18; the date the board fits best: 30 June
  disagrees on 239 records, opening day on 691). Birth dates by MLBAM id (gn_mlb_people_2026.csv), then
  v51.13's guarded name match, then FanGraphs eng.bd. 239 ages disagreed; 238 are corrected.
      T4 168 (149 a year younger), T3 35, T1 21, T2 8, T5 6; 206 are below peak age once fixed.
      Off by two or more: Luis Hernández (T4) 23 -> 17 (the June age fix had matched a different Luis
      Hernández), Bradgley Rodriguez (T3) 26 -> 22, Javier Sanoja and Jack Wenninger (T1) 3 years younger,
      Caden Scarborough, Zach Fruit, Trey Gregory-Alford (T4) and Austin Warren (T1) by two.
  Every changed line is rebuilt on its corrected age with v51.16's methods: the growth ramp below peak age
  (peak cell = Pure x pace), the age curve at or past it, a veteran's line re-indexed by his regression
  year with the cliff re-timed; PV-blended T4s through their pre-blend line (§21). 235 lines rebuilt.
  Where the corrected age changes the price, it follows: a production record's growth factor g(age), the
  Hit% healthy-base band, a veteran's regression clock. Every pre-peak production record now carries
  eng.g == g(a), which the season roll's growth step reads.

  RA MOVERS (33: 9 up, 24 down, net -159):
      Bradgley Rodriguez   26 -> 22   542 ->  646   growth 1.05 -> 1.25
      Trevor Williams      33 -> 34   491 ->  416   clock ry 6 -> 7
      Brady Singer         30 -> 29   769 ->  836   clock ry 3 -> 2
      TJ Rumfield          25 -> 26  1360 -> 1295   growth 1.05 -> 1.00
      Luke Keaschall       23        1150 -> 1202   his Pure still carried g(24) from the June age fix
      Cade Smith           26 -> 27  1086 -> 1035   growth 1.05 -> 1.00
      Jose Urquidy         30 -> 31   612 ->  563   Luis Torrens 29 -> 30   601 -> 553   Keegan Thompson 30 -> 31  600 -> 552
      Walbert Urena        23 -> 22  1111 -> 1157   Emerson Hancock 27  853 -> 812 (June age fix, growth never removed)
      Tony Gonsolin -21, Josh Rojas -14, Chase Silseth -13, Luke Jackson +13, Max Schuemann -12,
      Daniel Schneemann -11, Trey Sweeney -10, Logan Evans -10, David Sandlin +8, and 11 more by 5 or less.
  Board ten-year sum 5,496,951 -> 5,500,332 (+0.06%).

  ONE BANKED PEAK WITHOUT ITS GROWTH FACTOR. Max Muncy (Ath), T3 production, 23: the in-season ratchet
  banked his 2026 to-date total as the ceiling with g(age) left out (Pure 337 = peak 337) and started his
  regression clock at 23. §19.3/§19.6 price a pre-peak production ceiling at best season x g(age):
  Pure 337 -> 387.5, clock start 23 -> 27, RA 269 -> 310. He is the only record the rule matches.

  HELD OR FLAGGED (for the commissioner):
    - Five T1s are now below peak age by birth date: Javier Sanoja 23, Ben Williamson 25, Victor Vodnik 26,
      Angel Zerpa 26, Jack Wenninger 24. They stay T1, their lines flat until their regression start;
      Wenninger also has no MLB debut on record, so §4 would read him as a T4.
    - Two MLBAM ids are on the board twice: 687209 (Zach Maxwell, Zachary Maxwell) and 678606 (Jose Ferrer,
      José A. Ferrer). Zachary Maxwell's age fix is held until membership is settled.
    - Four birth dates differ between MLBAM and FanGraphs (Zach Fruit, David Davalillo, Trey Gregory-Alford,
      McCade Brown); MLBAM is used. They, with Zachary Maxwell, are build.json age_audit.residual -- the
      season roll refuses unless its own age check finds exactly these.
    - 45 records have no birth date from any source (Kershaw, Darvish, Pablo Lopez, Santander, Rizzo ...);
      a people-pull top-up for T1/T2/T5 names needs network access.

================================================================================
3. THE APP SAYS WHICH SEASON EACH CELL IS                 patch_season_aware_v51_17.py

  No value changes on any record the age fix did not touch (228,744 getValue results, 4,236 Inspector
  panels, every chart config compared against v51.16).
  - Trajectory cells read 'Current / 2026', 'Y2 / 2027' ... with the year on its own line; the star, the
    age line and the value are where they were.
  - Injury year labels read GN_INJ_OPENING (build.json injury_opening), not data-through + 1. Until the roll
    the Inspector says the Current (2026) cell carries the module's 2027 line; after it, that they align.
  - Every label that means "the current season" reads GN_NOW_Y ('2026 pace', 'banked 2026 to-date', the
    Options Tracker heading, the 2026 view button); dated history keeps its dates.
  - Ready for the roll: when GNDAILY carries a season stamp the season view becomes the frozen '2026 season
    (final)' archive drawn on its own RAW; when GNROS carries one, ROS mode is switched off with a note; the
    recency-floor block reads the roll's eng.rf and the archived 2026 pace.
  - build.json gains injury_opening, season 2026 and age_audit {season 2026, build v51.17, residual}.

================================================================================
4. THE WORKBOOK

  Re-synced by resync_ceiling_workbook_v51.17.py (v51.16's, admitting exactly the corrected ages and the
  repriced records, read from the v51.16 board).
  2_Org_Rankings recomputed (River Cats 54,334 still first, KC Gray Hotdogs 50,802 second).

================================================================================
5. THE SEASON ROLL (built, not run)

  season_roll.py replaces season_roll_lambda_v51.11.py (withdrawn; its --apply always refuses) and
  make_roll_v51_11.py (withdrawn). It advances the whole board a season -- ages, regression clocks,
  trajectories shifted a year, pace multipliers reset, Hit% re-assembled at the new age, the §4 tier moves,
  injury weights recomputed on the shifted lines -- and runs §13.1's carry, unchanged, where it applies.
  It writes only to --out; promotion to calc/ is a separate step after verify_calc.py --roll is FAIL 0 and
  the commissioner's OK. It refuses before the season is complete, without this age audit, or on any
  identity it cannot prove. Rehearsed on copies of the board; to be run on the final 2026 pull.

================================================================================
6. GATES

  build_v51_17.py   round trip; v51.16 guard (tj, ia, r reproduce); after: tj, r, im == ia, d, every ramp at
                    its peak age, every T3-T5 line past peak on its age curve, no line moved on a record
                    whose age and price did not; every patch anchor matched once.
  Browser sweep     both pages over http from a scratch copy: 2,118 panels x 2 bust-risk modes, 42,360
                    cells equal fadeAdjustedTj, each cell's age and season right, one ★ at the peak index
                    (2,113; five players aged 16-17 peak past the grid), every value-over-time line equal to
                    the grid; no page errors.
  verify_calc.py    FAIL 0, WARN 2 -- the standing designation-lag warning and the 9 T3s on a veteran basis.
                    New since v51.16: it checks GN_INJ_OPENING against build.json and the injury feed, derives
                    its season dates from build.json, and has a --roll mode for the season roll.

================================================================================
7. STILL OPEN

  * The five T1s below peak age, the duplicate MLBAM records and the four birth-date conflicts (section 2).
  * Before the roll: the final 2026 pull and weekly refresh, the injury module re-run on the post-season
    feed, the regular season's end date in build.json, then season_roll.py.
  * How pace multipliers reopen in 2027 (the weekly script; the roll resets them all to 1.00).
  * McKenzie/Garrett, REPACE and the 9 T3s on a veteran basis (from v51.13).

RUN ORDER TO REPRODUCE
  python3 build_v51_17.py --apply            # calc/ (backups *.pre-v51_17), build.json, board, report
  cp README_v51.17.txt calc/README.txt       # README_v51.16.txt moved to notes/
  python3 resync_ceiling_workbook_v51.17.py --apply
  python3 verify_calc.py
  python3 package.py --apply

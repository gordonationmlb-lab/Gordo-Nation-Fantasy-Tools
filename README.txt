GORDO NATION TRADE CALCULATOR — v51.15  THE YOUNG STOP LEAVING THE LEAGUE EARLY (2026-09-23)
  Built on v51.14. Same pull and data window: scoringPeriod 173, matchup period 22, Week 22 data.
  Rosters through 2026-09-22 (scoringPeriod 182), unchanged from v51.14. No weekly refresh ran.
  Service worker: gordo-calc-v88-2026-09-13-v51.15.  GN_BUILD v51.15, GN_DATA_THROUGH 2026-09-13,
  GN_ROSTERS_THROUGH 2026-09-22.
  Acceptance: verify_v51_15.js PASS (6 checks); verify_calc_v51_15.py FAIL 0 (WARN 2, both standing);
  render_check_v51_15.js 2,118 panels x 2 fade modes, 0 problems, 0 page errors.
  RAW_PER_DOLLAR 536.61 -> 536.52.

================================================================================
1. WHAT PROMPTED IT

  Commissioner, 23 Sep, off the Player Inspector: Jackson Holliday is 22, four seasons short of his
  age-26 peak, and every cell of his ten-year trajectory is lower than the one before it.

      v51.14   925   914   882   836   805   714   610   465   356   272

  The playing curve underneath it does ramp -- tjp x Hit% x injury reads 925, 982, 1026, 1076,
  1130 at 26, then 1072, 1019, 918, 844, 777. All of the decline is the §14.1 attrition term that
  v51.11 added, P(still producing in MLB in year k):

      tj[k] = tjp[k] x Hit%(age+k) x inj_factor(k) x att(age, k)

  Holliday is not special. Of the 923 players two or more seasons short of peak whose playing
  curve rises, 901 had an expected curve that never once exceeded year 0.

================================================================================
2. THE DEFECT -- the young rows were the chained hazard the fit had rejected

  hazard_fit.py fitted a logistic in (k, age, k*age, k^2, age^2) and then applied two one-sided
  constraints. Both bind on the young, and both in the wrong direction:

  (1) Every in-horizon year was capped at the one-year hazard of a FRESH anchor of the attained
      age. It was meant to remove the k^2 upturn. For ages 19-25 it binds on every year from k=2
      (from k=1 at 23-25), so those rows ARE the chained one-year hazard -- the form the same
      file's docstring rejects. The comment beside the cap says the young's risk is "front-loaded
      (does he stick?)". Front-loaded risk means a survivor's later years are SAFER than a fresh
      anchor's. The cap forbids exactly that.

  (2) One pooled frailty factor, 0.913 (the median over ages 19-43), was carried into the tail for
      every age. Ages 19-28 each fit a horizon ratio of 1.01-1.12: their survivors are sturdier
      than a fresh anchor of the attained age, not frailer.

  Age 22, years 1-5:         the fit   0.930  0.899  0.870  0.852  0.849
                             v51.14    0.930  0.859  0.777  0.713  0.665
  Observed, <=24 band (Deferral_Discount_Ruling.md §4):
                                       0.926  0.872  0.871  0.807  0.770
  v51.11's own docstring says "0.770 five-year survival at age 24". It shipped 0.675 for 24.

================================================================================
3. HOW IT WAS FIXED WITHOUT THE ORIGINAL DATA           attrition_fix_v51_15.py

  discount_pairs.csv, the 6,899 pairs the surface was fitted on, was never saved to the league
  folder. It is not needed: every cell of the v51.11 table where no constraint bound IS the
  logistic, so an OLS on the logit of those cells returns the coefficients.

      63 unconstrained cells, max |error| 0.00008 (four-decimal rounding is 0.00005)
      ROUND TRIP: the v51.11 rules applied to the recovered fit reproduce all 325 shipped cells
      to within 0.0001, and the pooled frailty to 0.9129 exactly.

  The correction relaxes each constraint only where an age's own fit contradicts it:
      fr(a) = [s(a,5)/s(a,4)] / h(a+4)     the age's fitted horizon ratio
      in-horizon  fr(a) >= 1 (ages 19-28): capped at 1.0, i.e. monotone in k -- all the k^2
                  upturn ever needed. Ages 29+ keep the attained-age cap.
      tail        frailty(a) = clip(fr(a), 0.913, 1.0): 1.0 for 19-28 (the raw attained-age
                  hazard, NOT their fitted excess), 0.985 at 29, 0.943 at 30, 0.913 from 31.
  Ages 31-43 are byte-identical to v51.11. Every cell is >= its v51.11 value. Monotone in k and,
  past 27, in age: zero violations.

  Against the observed band table (each band weighted by the age mix of the 4,689 qualified MLB
  player-seasons 2019-2024 in the xFP Anchor Study files -- a proxy for the anchors' own mix,
  which went with discount_pairs.csv):
      mean |error|, all 25 cells     v51.11 0.0288   v51.15 0.0206
      mean |error|, <=24 band        v51.11 0.0651   v51.15 0.0191
  0.0206 is, to rounding, the 0.0204 hazard_fit.py reports for the logistic -- that figure was the
  fit's, before the cap; the shipped surface was never re-scored after it.

================================================================================
4. WHAT MOVES                                          apply_attrition_v51_15.py

  tj on 1,650 records (everyone aged 19-30). Year 0 on none: att(age, 0) = 1 by construction.
  The asset multiplier ia weights its years by attrition (v51.11), so 380 injured records re-weight
  and 92 of them move RA -- all up, by 1-13 points: Hunter Greene 922 -> 935, Cade Horton
  673 -> 685, Chase Dollander 867 -> 878. 66 dollar figures move, by 1 to 3 cents.

  RAW_PER_DOLLAR, re-floated by the standing rule (mean r over the eid-bridged pool, r > 0):
      536.61 shipped -> 536.40 on v51.14 as it stands -> 536.52
  The first step is v51.14's: it bridged four eids and, being roster-only, did not re-float.
  This build's own effect is +0.12.

  Ten-year expected RA (the Cumulative and single-year views; the headline is year 1 and is not):
      age <=22   +20.8%     23-25 +12.4%     26-28 +3.5%     29-30 +0.8%     31+  0.0%
      board      3,873,745 -> 4,168,655 (+7.6%)
  Players aged 24 or under whose expected curve ever rises above year 0: 15 -> 483.

      Jackson Holliday 22   v51.14   925  914  882  836  805  714  610  465  356  272
                            v51.15   925  914  922  936  962  910  813  679  569  477
      Konnor Griffin   20   v51.14  1106 1028 1006  983  949  899  828  671  547  417
                            v51.15  1106 1028 1043 1068 1109 1162 1120  993  887  740

  Holliday's Y2 cell still sits under his Current cell: his playing curve rises 6.2% (925 -> 982)
  and a 7% chance of being out of the majors next season takes back slightly more. From there the
  curve climbs to his age-26 peak, as it should.

  DISCLOSURE. Org ten-year expected RA: C-Town Liquors +12.0%, River Cats +11.5%, KC Gray
  Hotdogs +6.3%, High Cheddar +5.1%, Kansas Sunflower Seeds +4.6%, Dirty Spikes +3.4%, Balking
  Dead +3.4%, MidwestBears +2.3%. The commissioner's own club gains the most, because it holds the
  youngest core. Org RA (the headline) moves by 0 to +19 points.

================================================================================
5. THE INSPECTOR

  The grid printed tj under "RA, ramping toward peak then regressing" -- a promise the numbers
  stopped keeping in v51.11, and the reason the question was asked. Each cell now carries:
      top    expected RA -- unchanged in meaning, and what every $ and cumulative view uses
      grey   the playing curve alone: the cell / gnAttFactor(p, k)
  and a note row under the grid gives the attrition by year for the player's age. The same holds
  in the bust-risk-off view, where the grey line is the released curve before attrition.

================================================================================
6. GATES

  attrition_fix_v51_15.py   recovery error, round trip, monotonicity, 31+ identical, never below
                            v51.11, and the <=24 band must improve -- or nothing is written.
  apply_attrition_v51_15.py round-trip guard (v51.14's board re-serialises byte-identically);
                            old-surface guard (tj, ia and r of all 2,118 records reproduce from the
                            v51.11 surface BEFORE anything changes); then tj, r, im == ia, ia inside
                            its season lines, d == r/RAW, 31+ unmoved, year 0 unmoved, no cell down.
  verify_v51_15.js          1  every byte outside the six intended edits and renderInspector identical
                            2  GN_ATT == attrition_table_v51.15.json; 31-43 identical to v51.14
                            3  the risk-adjusted grid reads tj; 31+ and year 0 untouched (21,180 cells)
                            4  bust-risk-off moved by exactly att_new/att_old (10,850 T3/T4 cells);
                               the released cell still dominates, worst overhang 0.95 pts; the
                               release cap holds, tightest headroom 13.6
                            5  the grey line == tjp x Hit% x injury, within rounding
                            6  renderInspector: only the h4, the grey line and the note row changed
  verify_calc_v51_15.py     verify_calc_v51_14.py with the attrition import moved to v51.15.
                            FAIL 0, WARN 2 -- line for line what v51.14 prints in the same harness,
                            bar the build, RAW and cache stamps. Negative control: the v51.14 gate
                            (v51.11 surface) run on this build FAILS 1,570 tj and 68 ia records.
  render_check_v51_15.js    headless Chromium over http, every panel in both fade modes: top line
                            == fadeAdjustedTj, grey == top / gnAttFactor (blank in Current), the note
                            names the right age and nine percentages, no h4 promises the ramp.
                            2,118 panels, 21,180 cells per mode, 0 problems, 0 page errors.
                            Renders: Claude outputs/v51.15 - Attrition Young Rows/.

================================================================================
7. NOT DONE, AND STILL OPEN

  * The old-age direction. Ages 33+ fit horizon ratios of 0.89 down to 0.48 -- their own fit says
    the tail is STEEPER than the pooled 0.913 charges. That is real and would cut veterans. It
    wants its own ruling, not a rider on a young-player fix.
  * Quality. The surface is age-only: an everyday 22-year-old and a September call-up of the same
    age carry the same exit rate, and for a prospect the clock starts now rather than at arrival.
    Conditioning on the anchor season needs discount_pairs.csv rebuilt -- and saved this time.
  * build.json still carries v51.13 expectations (shared workspace). build_v51.15.json holds this
    build's; verify_calc_v51_15.py was run in a copy with it as build.json, calc/ as this build
    plus gn-history.js, and this README as the only README*.txt.
  * The CEILING workbook and Issue 24 were NOT re-synced. Headline RA moved on 92 records by at
    most 13 points; the multi-year views moved as above.

RUN ORDER TO REPRODUCE
  python3 attrition_fix_v51_15.py --write        # -> attrition_table_v51.15.json, gn_attrition_v51_15.py
  python3 apply_attrition_v51_15.py --apply      # -> ../GordoNation_Calculator_v51.15/
  node verify_v51_15.js ../GordoNation_Calculator_v51.14/gn-app.js ../GordoNation_Calculator_v51.15/gn-app.js attrition_table_v51.15.json
  python3 verify_calc_v51_15.py                  # in a copy, see section 7

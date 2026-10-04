GORDO NATION TRADE CALCULATOR — v53.0  THE RATE-BASED ENGINE INSTALLED (2026-10-03)
  Built on v52.0 by build_v53_0.py: every price is rebuilt on the rate-based engine, exactly the verified shadow
  default H3|S2-lite|P-hold|T5a (the commissioner's "install now" of 3 Oct 2026; the Sitting B defaults stand, D-5).
  Same data window: data through 2026-09-27 (scoringPeriod 187); TEAM_GAMES 162, F = 162/162 = 1.0000 (as v52.0).
  Current stays the 2027 season (GN_NOW_Y 2027). 2026 is the newest history season of every price, shown as a greyed
  "2026 actual" cell before 2027 (D-1). The 2026 season view stays the frozen v52 archive.
  Service worker: gordo-calc-v96-2026-09-27-v53.0.  GN_BUILD v53.0, GN_DATA_THROUGH 2026-09-27,
  GN_ROSTERS_THROUGH 2026-09-27. Injury line opens 2027-03-25 (the injury module is not re-run).
  Model: model/gn_rate_model_v1_cur_refit_2000_2026.json (sha256 c7829868...), fitted on 2000-2026, 2020 excluded.
  Acceptance on the staged folder ../v53_staging/v53.0: check_v53_0.py PASS, 0 disagreements; the e = 0 spike
  (rate_engine.py) 0 mismatches; verify_calc_v53.py FAIL 0; render, values and compare checks pass.
  RAW_PER_DOLLAR 510.28 -> 371.69.
================================================================================
1. WHAT v53.0 IS, IN PLAIN WORDS

  v52.0 priced a player from his best season: a "Pure ceiling" (his peak production), then cut it by a Hit% (the
  chance he gets there) and an injury multiplier. v53.0 prices what a season is expected to be worth:

    Pure  = the expected healthy full season: his MLB scoring rate (FP per PA or per IP, blended over his last three
            seasons and pulled toward the league by how much evidence there is) x a full season's playing time for
            his role (a hitter's 153 games, a catcher's about 135, a starter's 32.5 starts, a reliever's 70 games),
            x 1.15 at C, 2B and 3B (scarcity).
    Hit%  = the share of that full season he is expected to play, including the chance he has left MLB (availability
            x survival, from a model fitted on every MLB season 2000-2026). It can exceed 100% for an everyday
            player (44 headlines do, Corbin Carroll highest at 117.77%).
    RA    = Pure x Hit% x the injury multiplier, the same three-part identity as before.

  The headline (the one-number value) prices his peak-age season, counting the chance he has left MLB by then (H3):
  the season k* = min(9, max(0, peak - a0 - 1)), peak 26 for hitters and 27 for pitchers. The ten-year line is the
  same calculation season by season. pm (the pace multiplier) is 1.00 on every record.

  Who is priced how (2,118 records):
    1,224  on MLB rates from scratch (S1)
      216  prospects with MLB time, priced on MLB rates starting from their prospect value (S2-lite; the 198 tool T3s
           with MLB time plus the 18 switched at the v52.0 pre-roll step)
      675  prospects without MLB time: the v52.0 prospect price x kappa_P (P-hold, kappa_P 0.7284; it holds the
           prospects' headline dollars where v52.0 had them)
        3  held at their v52.0 values (no MLB id match: Jack Wenninger, Luis Ortiz, Jose A. Ferrer)

  What a manager sees: the Player Inspector shows the new chain (rate, playing time, Hit% = availability x survival,
  injury), a greyed "2026 actual" cell before the ten seasons, and a link to the model-tables page
  (gn-model-tables.html). The term-by-term detail loads on demand from gn-rate-detail.js. The Trade Desk, the
  slider and Compare read the same numbers. The slider's Pure end applies to the one-season view only.

2. THE BOARD IMPACT (measured on the staged board against v52.0; $ = value / RAW)
  Dollars as the page defaults compute them: headline $ = r / RAW; 5-year $ = max(sum tj[0..4], r) / RAW;
  10-year $ = max(sum tj, r) / RAW. "Moved" = by five cents or more.

    all 2,118     v52.0 (510.28)   v53.0 (371.69)     change     RAW held at 510.28     players moved
    headline         $1,574.47        $1,615.30    +$40.82 (+2.6%)    $1,176.59 (-25.3%)    1,312 (731 up, 581 down)
    5-year           $6,503.69        $6,216.76   -$286.93 (-4.4%)    $4,528.32 (-30.4%)    1,748 (626 up, 1,122 down)
    10-year          $9,785.55        $8,696.19 -$1,089.35 (-11.1%)   $6,334.34 (-35.3%)    2,089 (521 up, 1,568 down)

  On the displayed (rounded) d, 1,325 players move by five cents or more on the headline.

  RAW falls from 510.28 to 371.69. The new engine prices an expected season, not a best season, so raw points fall.
  RAW is the mean RA over the records with an ESPN id and RA > 0: 1,402 such records at v52.0, 1,445 now. Over the
  same 1,402 the v53.0 mean would be 380.39; the rest of the fall comes from the 43 records that now price above zero
  and join the pool (none leaves it).

  After the re-float the headline total barely moves, but the 5-year and 10-year totals fall: the engine expects
  fewer future seasons from the players on the board, mostly the older ones.

  The 406 rostered players together: headline $709.25 -> $800.26 (+$91.01, +12.8%); 5-year $2,934.00 -> $3,052.18
  (+$118.18); 10-year $4,334.49 -> $4,210.85 (-$123.65). Their average headline RA goes from 891.42 to 732.63.

  CLUBS (RA and headline $, v52.0 -> v53.0; ordered by v53.0 RA):
    River Cats              54,604 -> 45,410   $107.01 -> $122.17
    KC Gray Hotdogs         49,548 -> 43,020    $97.10 -> $115.74
    Kansas Sunflower Seeds  46,239 -> 38,834    $90.61 -> $104.48
    Dirty Spikes            43,569 -> 37,088    $85.38 ->  $99.78
    MidwestBears            42,236 -> 34,841    $82.77 ->  $93.74
    High Cheddar            43,234 -> 34,524    $84.73 ->  $92.88
    C-Town Liquors          42,223 -> 32,852    $82.74 ->  $88.39
    Balking Dead            40,263 -> 30,880    $78.90 ->  $83.08
  (High Cheddar and MidwestBears swap 5th and 6th; every other club keeps its rank.)

  THE CEILING WORKBOOK: resync_ceiling_workbook_v53_0.py (pure stdlib) re-writes 1_Player_Inputs on the rate basis
  (column 9 is the priced Hit%, U at k* moves to a new column, pm is 1.00 everywhere, A_rec is 0) and rebuilds the
  prospect sheets 7 and 12. The file name is kept (D-5).
  2_Org_Rankings recomputed (River Cats 45,410 still first, KC Gray Hotdogs 43,020 second).

3. THE LARGEST MOVERS (headline $, v52.0 -> v53.0)
  Up:   Shohei Ohtani $3.45 -> $5.60; Corbin Carroll $2.42 -> $3.90; Jose Ramirez $1.55 -> $2.99; Bobby Witt Jr.
        $2.61 -> $4.01; Ketel Marte $1.86 -> $3.26; Rafael Devers $2.01 -> $3.27; William Contreras $2.28 -> $3.53;
        Max Meyer $1.52 -> $2.74; Jazz Chisholm Jr. $1.67 -> $2.88; Yoshinobu Yamamoto $2.96 -> $4.15.
  Down: Mike Clevinger $1.63 -> $0.02; Cristian Javier $2.14 -> $0.69; Alexis Diaz $1.47 -> $0.06; Triston McKenzie
        $1.61 -> $0.21; Dylan Carlson $1.64 -> $0.25; Jack Suwinski $1.46 -> $0.10; Tim Anderson $1.29 -> $0.02;
        German Marquez $1.58 -> $0.33; Jackson Jobe $2.49 -> $1.28; Trey Yesavage $2.60 -> $1.40.
  The big drops are players whose v52.0 price came from a past peak that their recent MLB rates and playing time do
  not support; the big rises are everyday regulars whose expected season is worth more than v52.0's ceiling read.

4. THE HANDOVER AND THE PROSPECTS
  - The handover switch fired. SPEC 10 declared in advance: if the median value jump of the 18 players switched at
    the v52.0 pre-roll step lies outside +/-10%, the gradual handover (S2-lite) replaces the one-day switch (S1).
    Under H3 the median jump is +40.8%; 13 of the 18 jump by more than 30%: A.J. Ewing +72.1%, Henry Bolte +204.3%,
    Carter Jensen +67.4%, Carson Benge +30.6%, Logan Henderson +38.3%, Travis Bazzana +50.4%, Jacob Gonzalez +218.9%,
    Hao-Yu Lee +131.0%, Kumar Rocker +43.3%, Spencer Miles +200.0%, Jake Bennett +30.9%, Cole Carrigg +115.7%,
    Didier Fuentes -38.1%. (Measured on the pinned shadow board, sha256 57a225b2..., which this build reproduces.)
  - So the 216 prospects with MLB time (198 + 18) are priced on MLB rates starting from their prospect value.
  - The 675 others keep the v52.0 prospect chain x kappa_P (P-hold). The branch's share of the board's cumulative RA
    is 10.4% at 1 year, 12.2% at 5 years and 14.9% at 10 years (verify G11).
  - The 8 relievers who graduated at v52.0 (Cole Winn, Will Klein, Sam Bachman, Seth Halvorsen, David Morgan, Carlos
    Vargas, Roansy Contreras, Mason Englert) are T1 rate records now, priced from their rates with no x0.80.
  - The D8 maturation x0.80 stays as a named Inspector line on the 8 production T3s that carry it (Kristian
    Campbell, Jack Kochanowicz, Hurston Waldrep, Chase Silseth, Robert Hassell III, Luis Matos, Logan Evans, Jonathan
    Cannon). The 3 switched Book records (Jacob Gonzalez, Jake Bennett, Ryan Johnson) are S2-lite at 1.0 (RD 6).

5. RECORDS THAT NEED ATTENTION (plan 2.11; each is named in the build report, build_report_v53_0.json)
  - Pricing age differs from board age, 10: the history age prices (the board ages were "fixed first" at v51.17 and
    are not changed here). Hayden Birdsong (board 29, a0 24, k* 2), Porter Hodge (29, 25, k* 1), Reese Olson (28,
    26), David Festa (29, 26), Gunnar Hoglund (29, 26), Mike Vasil (28, 26), Hector Neris (37, 37), Chad Green (35,
    35), Andrew Saalfrank (28, 28), Bowden Francis (30, 30). The Inspector prints a0 and its source.
  - No 2026 row, 92 player-kinds (86 newest 2025, 6 newest 2024), e.g. Justin Steele, Anthony Santander, Spencer
    Schwellenbach, A.J. Puk, Edwin Uceta, Robert Stephenson, Pablo Lopez, Frankie Montas. Their newest row carries its
    own lag weight; the "2026 actual" cell reads "2026: no MLB units (0)".
  - Newly priced free agents, 38 (no injury-module record at v52.0; each gets the minimal injury block). Two of them
    are on an ESPN list: Jonathan Heasley (IL-60) and Wyatt Mills (OUT).
  - Bridged to MLB by a unique name, 44; 10 of them are the 10 pricing-age records above (an unaudited board age).
  - Hit% above 100%, 44 headlines (max 1.1777, Corbin Carroll): an everyday player's expected share can exceed the
    full-season playing-time unit. The Inspector explains it.
  - Priced in the other pitcher group, 91 (a one-kind pitcher whose kind differs from the board position): S1 board SP
    priced RP 34; S1 board RP priced SP 21; S2-lite board SP priced RP 31; S2-lite board RP priced SP 5. The Inspector
    prints "priced as <group>".
  - A history row's group differs from the kind's group: 123 rows on 105 records (e.g. Nick Martinez's 2024 RP row).
    Each row is valued in its own group's league rate.
  - Held at v52.0, 3: RA unchanged; their dollars re-float against 371.69: Jack Wenninger RA 24, $0.05 -> $0.06; Luis
    Ortiz RA 70, $0.14 -> $0.19; Jose A. Ferrer RA 150, $0.29 -> $0.40. The panel says "v52.0 scale".
  - No birth date on file, 40 records (no eng.bd, no eng.aod, and no MLBAM date for eng.mid): deferred to the 2027
    roll. Rate prices use the history age. (The plan's earlier count was 45; this is the count on this board.)
  - ESPN designation vs the injury module, 25 rows, all unrostered free agents carried unchanged from v52.0; nothing
    is repriced for them at v53.0 (verify WARN; listed in V53_REVIEW.md).
  - Five branch values sit on an exact half (pc x 0.2 = .5): Gabriel Rodriguez, Anthony Millan, Jose Manon, Pedro
    Blanco, Daury Vasquez. Each prints its stored RA.

6. WHAT IS NOT IN v53.0 (deferred, each by name)
  - The fielding line: fld = 0 on every record (deferred to phase 12).
  - The evidence rule (drop the 15 appearances before an IL placement from a pitcher's row): deferred, because no
    per-appearance source exists. 88 rate pitchers carry the exposure (on an injured list with R or R2 set), 60 of
    them with 2026 innings. Reported weekly from v53.1 (D-3).
  - G9, the double-count audit: REPORTED, not blocking (ruled 3 Oct; a property of the model). (a) the scoring rate
    tracks last season's playing time: hitters +0.156, starters +0.105, against 0.10; (b) the share model's errors
    track the rate: all -0.052, hitters -0.061, relievers -0.098, against 0.05.
  - G14 (roll continuity) and G17 (weekly churn): not run at v53.0; they need the in-season engine (v53.1). G14's
    newcomer-prior reading is open (D-2). No installed record is a newcomer at e = 0.
  - N-1: no level adjustment for players back from injury now; the returners are checked as a group after the 2027
    season (ruled 1 Oct).
  - The MLB terms question is still unruled (D7).
  - Keeper values move by design (getKval reads tj). The confidence labels are v52.0's.
  - The Inspector's term-by-term breakdown is at the headline season; the other nine seasons show their values and
    U / SIGMA / A, not the logit terms.
  - The weekly refresh is NOT runnable on a rate board until v53.1 (target 5 Feb 2027, hard stop before opening day,
    25 Mar 2027). The v52 weekly and one-time scripts refuse a rate board (engine_guard.py). In v53.1 the weekly
    script itself changes (update_calc_weekly.py v53: preflight, the bridge, rosters and designations, the
    season-to-date rows, then rate_engine.price_board; plan 7.2), followed as now by verify_calc.py, stamp.py and
    package.py. A roster-only refresh (no repricing) comes first, in v53.1's first round (D-4).
  - 30 one-time scripts moved to archive/one_time_v51/ fail closed by folder. The two season_roll_lambda records do
    not, and are documented as such: each takes the board path on argv and still requires --apply
    --confirm-season-complete.

7. CHECKS RETIRED OR DEFERRED (verify_calc_v53.py prints this table on every run)
  - tj identity with _hit_at, the asset identity w = tjp x _hit_at, the _hit_clean assembly: REWRITTEN as G3 / G5 /
    G10 on rate records (Hit% is U per season, not a band shift); kept on branch and held records.
  - The age-mate curve and _CLOCK_HELD; "tjp peaks at kp"; the pace-gate leak; "WARN T3 on a vet basis": RETIRED
    (rate lines are closed form; G4 replaces the peak test; pm is 1.00; no vet basis outside the 3 held).
  - PV blend, injury carve-out vs basis, TIER / BASIS map: REWRITTEN (narrow) for the rate basis.
  - The --roll checks (REG, cliff, g, clock, carry, ratchet, floor, --rulings-v52): MOVED with the v52 verify to tag
    v52.0 and the standby; the v53 --roll refuses a rate board.
  - The KEEP-class roll checks (age / aod / bd +1, il / ir unchanged, inj.f untouched, tier labels, rotation, roster
    fields): DEFERRED to the rate roll (phase 12).
  - The Inspector chain check: REWRITTEN as X-RC (render_check_rate1.js). inspector_equiv_v51_19/20.js,
    inspector_check_v51_18.js and render_check_v51_15.js: RETIRED (kept as records, never run).
  - NOT RUN at v53.0: G14, G17, G13-live (v53.1).

8. ROLLBACK
  Until opening day, build_v53_0.py --rollback restores every tracked build-folder file outside redesign/ from tag
  v52.0 (from git, not from backups) and removes what v53.0 added, except model/, v53_archive/, redesign/ and the v53
  scripts outside calc/ (provenance; nothing on the v52 path reads them). redesign/ (the decision records and the
  spec) is exempt: the rollback never restores, removes or rewrites a path under it (R4b-1). The v52 verify then gives
  FAIL 0 WARN 2, stamp.py finds its v52 phrase, and package.py rebuilds the 21-entry v52.0 zip;
  GordoNation_Calculator_v52.0.zip is unchanged on disk and is what the commissioner re-uploads. From opening day to
  the ROLLBACK DEADLINE, SAT 1 MAY 2027, a rollback runs the v52 hot standby (v53.1, S7). After 1 May 2027 the project
  fixes forward.

9. THE SHADOW ENVIRONMENT (how the prices were produced and can be reproduced)
  The pinned shadow board (board_shadow_v52.0.json, sha256 57a225b2...) is reproduced byte for byte from
  git archive of 413917f (tag v53.0-shadow-env) plus two untracked inputs; the commands are in
  v53_archive/INPUTS_v53.0.json (shadow_env.commands and run_commands) and in v53_archive/RELEASE_v53.0.md.
    cd redesign/shadow && python3 -B shadow_price.py --model model/gn_rate_model_v1_cur_refit_2000_2026.json --out ...
    cd redesign/shadow && python3 -B shadow_verify.py --derive --model model/gn_rate_model_v1_cur_refit_2000_2026.json
    or all of W0 from a clean environment: python3 -B freeze_v53_0.py all; then python3 -B freeze_v53_0.py --check

RUN ORDER TO REPRODUCE THE PROMOTION (branch calculator-v53.0; one step at a time, never in parallel)
  On the STAGE (A-R4-1: W2, then the spike, then --record, then W3; never W2 into STAGE after --record):
  python3 -B -I build_v53_0.py --out ../v53_staging/v53.0 --built 2026-10-03 --utc <the run time>   # 4 stages
    (--utc is the release run's own UTC time, recorded in build.json; the build is dated the promotion date)
  python3 -B -I check_v53_0.py --stage ../v53_staging/v53.0 --expect-combo 'H3|S2-lite|P-hold|T5a'
                                                                                   # PASS, 0 disagreements
  python3 -B -I rate_engine.py --spike ../v53_staging/v53.0                          # 0 mismatches
  python3 -B -I build_v53_0.py --record ../v53_staging/v53.0
  python3 -B verify_calc_v53.py --root ../v53_staging/v53.0                          # FAIL 0
  (then, in parallel: render_check_rate1.js with the probe, values_check_v53.js, checks/compare_check_v53.js,
   page_v53/patch_values.py --selftest, test_engine_guards_v53.py --require-stage, the offline sweep)
  Then this README into the STAGE root, and verify_calc_v53.py once more, alone.
  After the commissioner's OK on ../v53_staging/V53_REVIEW.md:
  python3 -B build_v53_0.py --promote ../v53_staging/v53.0 --date 2026-10-03 --approved '<the OK>'
  python3 -B verify_calc.py                                                        # FAIL 0
  python3 -B stamp.py --apply                                                      # writes the v53.0 as-of clause
  python3 -B stamp.py --check                                                      # exit 0 = clause once per page
  python3 -B resync_ceiling_workbook_v53_0.py --apply                              # then again: 0 cells
  python3 -B workbook_check_v53.py                                                 # every row equals the board
  python3 ../../../Reference/patch_methodology_v22.py --apply                      # Methodology v22
  python3 -B package.py --apply                                                    # GordoNation_Calculator_v53.0

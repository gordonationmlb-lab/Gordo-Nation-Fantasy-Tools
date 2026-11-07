GORDO NATION TRADE CALCULATOR — v53.1  THE IN-SEASON MACHINERY INSTALLED 2026-10-31; PRICES AS BUILT (2026-10-03)
  Installed on v53.0 on 2026-10-31 by the reviewed install tool (the commissioner's "start R9" of 31 Oct 2026, the GO
  for the v53.1 release). No price moves at the install: at e = 0 the v53.1 board is G13-live byte-identical to
  v53.0's, so every price, every dollar and RAW are v53.0's, and the date above stays v53.0's build date.
  What v53.1 adds: the weekly in-season repricing, the offseason roster-only refresh, the deploy label, the guards that
  hold the first 2027 weekly until its preconditions are met, and the rollback tool for this install.
  Same data window: data through 2026-09-27 (scoringPeriod 187); TEAM_GAMES 162, F = 162/162 = 1.0000 (as v53.0).
  Current is the 2027 season (GN_NOW_Y 2027); opening day is Thu 25 Mar 2027.
  Service worker: gordo-calc-v97-2026-09-27-v53.1.  GN_BUILD v53.1, GN_DATA_THROUGH 2026-09-27,
  GN_ROSTERS_THROUGH 2026-09-27. Injury line opens 2027-03-25 (the injury module is not re-run at the install).
  Model: model/gn_rate_model_v1_cur_refit_2000_2026.json, unchanged (the v53.0 model; combo H3|S2-lite|P-hold|T5a).
  Run with these scripts, each week in season (section 2 has the full order, W0 to W8): update_calc_weekly.py,
  news_facts.py, apply_injury_v2.py, update_calc_weekly.py --after-injury, update_options.py, stamp.py,
  resync_ceiling_workbook_v53_0.py --weekly (on a copy until R9c), verify_calc.py, package.py; and off season
  (section 4): update_calc_weekly.py --rosters-only, update_options.py, update_calc_weekly.py --deploy-label,
  stamp.py, verify_calc.py, package.py, manifest_check_v53.py.
  RAW_PER_DOLLAR unchanged at the install: 371.69.
================================================================================
1. WHAT v53.1 IS, IN PLAIN WORDS

  v53.0 (3 Oct 2026) put the rate-based engine live: a price is the expected value of a season, from a player's MLB
  scoring rate, his playing time and his chance of staying in MLB. v53.1 is the same engine with the machinery to run
  the 2027 season on it. Nothing is re-priced at the install: the board, the prices, RAW 371.69 and the CEILING
  workbook stay exactly as v53.0 left them. Methodology v23 (Reference/Trade_Calculator_Methodology_v23.docx) describes
  v53.1; it replaces v22.

  What changes when the season starts (after the season-start step, section 5):
    - each weekly refresh reprices the board on the season so far: e, the share of the 2027 season played, is read
      from the pinned 2027 schedule (v53_archive/inputs/hs_schedule_2027_R_f86a8c3e3e7f.json); the current season's
      cell becomes "to date + expected remainder"; the to-date row joins each player's rate evidence;
    - a hitter's playing-time class blends the two windows by e (C-R6-9), so it moves smoothly through the season;
    - a newcomer (a player-kind with no completed MLB season as of 2026) starts from the newcomer prior, whose weight
      falls by (1 - e) through the season (D-2 (b)); a new player with no MLB rows is a newcomer for 2027 (C-R8-2 (b));
    - the 216 S2-lite records keep their ceiling-based start (κ_P × tc) through 2027 and past the roll (D-6 (b));
    - injuries are priced by the frozen injury rules (C-R6-8); a suspension with games left at season's end counts
      against the next season (C-R8-1); a returning veteran keeps the frozen rule (C-R7-2);
    - each week verify measures the week's churn against the acknowledged G17 thresholds (a median move of 4%, a
      large-move mark of 87%, 0 star moves; g17_thresholds_2027.json). Over the median or the large-move mark is a
      WARN that means "look at this week's movers before publishing"; it never fails a build or changes a price. A star
      move is different: a record's ★ (its headline season k*) moving from install is over G17's star-move threshold
      and also FAILs verify's G4 (the star never moves in season), so that week stops at W7 (section 2);
    - the Player Inspector shows the in-season lines (this season's cell, the to-date line; display only, C-R7-1).

  Records added in season (plan 7.10 as ruled): a player with a completed MLB season in 2024-2026 is priced on MLB
  rates from scratch (row 1); a player with no completed MLB season is priced on rates as a newcomer (row 2; C-R8-2 (b)
  makes this the rule for 2027, whatever his prospect status); the frozen prospect branch (row 3) covers only the 675
  branch records already on the board. Off season the roster-only refresh adds no record: new players wait in pending_new.

================================================================================
2. THE WEEKLY RUN ORDER (in season; binding: PLAN_AMENDMENTS_R8 A-R8-3 item 2)

  Run from the build folder, one step at a time, never in parallel. P is the week's pull, <D> its data date.

W0  (operator) the ESPN pull into wk<yyyy>_<NN>/gordo_espn_pull_<date>.json, with gordo_espn_news_il_<date>.json beside it;
    and, when the week has them, the operator's declared facts in weekly_reports/declared_<D>.json (a ban's games and
    first missed date, a PR-C label: R-7)
W1  python3 -B update_calc_weekly.py <BUILD> --pull P --apply       also writes units_to_placement into declared_<D>.json
W2  python3 -B news_facts.py --apply
W3  python3 -B apply_injury_v2.py --apply --todate weekly_reports/todate_<D>.json --pull P
          --report weekly_reports/injury_<D>.json [--declared weekly_reports/declared_<D>.json]    (--declared whenever it exists)
W3b python3 -B update_calc_weekly.py --after-injury --apply
W4  python3 -B update_options.py --pull P --apply
W5  python3 -B stamp.py --apply ; python3 -B stamp.py --check          (S2c: the in-season path)
W6  python3 -B resync_ceiling_workbook_v53_0.py --weekly --root . --workbook <copy> --apply       copies only until R9c
W7  python3 -B verify_calc.py
W8  python3 -B package.py --apply                                   the four-copy rule holds after W8 (copy 3 is W8's output)

  Notes (each binding):
  - Each step first runs without --apply where it has a dry run, and the report is read before --apply. W2's dry run
    (news_facts.py without --apply) still writes its dated report, news_facts_report_<data_through>.json, and nothing
    else; its --apply refusal writes nothing at all.
  - The order: W2 before W3; W3 only after W1 has written the 2027 data_through; W3b after W3 and before W4; W6 after
    W3b. W1 writes the placement units into declared_<D>.json itself (W1b is gone); W3 passes --declared whenever that
    file exists, and always passes --report (it keeps C-R6-8's two counts).
  - No --standin-pre, ever: it is refused with --apply, and every W3 must exit 0 on its first run.
  - W5's EDITORIAL strings (stamp.py's header) are the operator's weekly judgement; in season stamp.py puts a
    generated in-season identity card on top of this file and leaves the install card below it as the record.
  - W6 runs on a COPY of the CEILING workbook until R9c (section 6): --weekly --apply refuses the real workbook (exit 2,
    nothing written).
  - The four README copies (this file, calc/README.txt, GordoNation_Calculator_<BUILD>/README.txt and the " 2" copy)
    are equal after W8. At W5 only the first two exist: copy 3 is W8's output, keyed by the week's new BUILD, and
    stamp.py names copies 3 and 4 as expected absent. Check copy 3 against this file after W8 --apply.
  - Exit codes of the logged writers (W1, W2, W3, W3b, W4, W6, the deploy label and update_options.py --rule5): 0 done;
    2 refused, nothing written; 3 board state unknown (a write failed and so did its restore). On 3, stop: nothing
    else runs until the pending log is resolved.
  - Exit codes of W5, W7 and W8 differ (none of them means an unknown board state):
    W5  stamp.py --apply: 0 written; 1 refused (nothing written, the reason named) or its read-back check failed.
        stamp.py --check: 0 every stamp current; 3 a stamp is not current (run stamp.py --apply again, then --check);
        1 refused.
    W7  verify_calc.py must report FAIL 0. WARN lines are allowed (G17's WARN, KEEP INJURY MODULE, the RULE5 line);
        read each one. Exit 1 means at least one FAIL (a star move is one: G4): stop there, no W8 and no upload; keep
        the output and ask the orchestrator. Exit 2 means the run itself was refused (nothing checked).
    W8  package.py: 0 done; 1 refused (it names why; there is nothing to upload).
    The upload follows only a W7 with FAIL 0 and a W8 --apply with exit 0.
  - The pending-log rule: every writer logs first (<log>.json.pending), then writes, then renames the log. A
    *.json.pending left in rosters_only_runs/, weekly_runs/, options_runs/, page_runs/, weekly_reports/ or injury_runs/
    is exit 3's state: every writer refuses while it exists and verify FAILs G13. Stop and ask the orchestrator.
  - Verify in BF: run it plain (python3 -B verify_calc.py). A --report path must be outside BF when the root is BF
    (verify refuses a report inside it). The same holds for every other --report of a check run on BF.

================================================================================
3. BUILD LABELS

  - In season: one new label per W1, v53.1-w<NN>, NN the 2027 refresh number from 01 (v53.1-w01, v53.1-w02, ...). A
    re-run of a week adds a letter (v53.1-w03b). W1 refuses a label the page already carries ("pick the next one").
  - Off season: v53.1.<n> (v53.1.1, v53.1.2, ...), written by the deploy label, never by hand:
        python3 -B update_calc_weekly.py --deploy-label v53.1.<n> --utc <YYYY-MM-DDTHH:MM:SSZ> --apply
    It writes the GN_BUILD literal, the .tc-sub build token and rosters date and the gn-build handshake of both pages,
    the service worker's cache name (the next number: v98, v99, ...) and SHELL, the GN_COMPARE_BUILD literal of
    calc/gn-compare.js, and build.json build, build_prev, sw_cache, sw_cache_prev; and a link log
    page_runs/PAGE_PATCH_<n>.json. No price moves. It refuses (exit 2, nothing written) a hyphenated label, a label
    already used, a weekly_runs/ log (in season each W1 labels its own build), a pending log, and --apply without
    --utc. The install itself labelled v53.1 this way.

================================================================================
4. OFF SEASON: THE ROSTER-ONLY REFRESH (D-4; usable in BF from v53.1 on, without --add-new)

  Precondition, once, before the first production roster-only --apply in BF: the orchestrator's v52-standby commit of
  S7b's R9 files (A-R9-14 item 3; the tid fix of S7b-R8c-F1) is done, and the standby's self-test (runbook S2) ends
  RESULT PASS with 90 check lines. Until both hold, no roster-only run is applied in BF.
  For a pull P placed as the operator places it (wk2026_off<NN>_<label>/gordo_espn_pull_<date>.json):
    python3 -B update_calc_weekly.py --rosters-only --pull P                         dry run: read the report
    python3 -B update_calc_weekly.py --rosters-only --pull P --apply                 rosters and designations; no price
    python3 -B update_options.py --pull P --apply                                    the options ledger (W4)
    python3 -B update_calc_weekly.py --deploy-label v53.1.<n> --utc <UTC> --apply   the new label (section 3)
    python3 -B stamp.py --apply ; python3 -B stamp.py --check                        exit 0
    python3 -B verify_calc.py                                                        FAIL 0
    python3 -B package.py ; python3 -B package.py --apply                            GordoNation_Calculator_v53.1.<n>
    python3 -B manifest_check_v53.py --dir ../GordoNation_Calculator_v53.1.<n> --manifest ../deploy_manifest_v53.1.<n>.json
  Then the commissioner uploads the 23 files as one commit (section 13), and the orchestrator runs the live check on his
  word. Then the standby replay of the new rosters_only_runs/ log (runbook S3, $BF/S7/ROLLBACK_RUNBOOK_v53.md),
  before the next roster-only run.
  - --add-new stays off in BF until R9c: --rosters-only --add-new --apply is refused (exit 2) in the live build folder.
    New players wait in pending_new and are priced by the first 2027 weekly.
  - Each step refuses while a pending log exists (section 2). Exit codes as in section 2: no package and no upload
    unless verify reports FAIL 0.

================================================================================
5. BEFORE THE FIRST 2027 WEEKLY: THE PRECONDITIONS

  No 2027 weekly runs in BF until all three are done. R9b comes before the season start, R9c by its deadline, and the
  season start last, before the first refresh:
  1. R9b, the 2027 Rule 5 list (C-R6-7 (d)): after the December 2026 draft, at the latest Mon 22 Mar 2027. The
     commissioner gives each pick (player, drafting club, original club) and the draft date (or says no draft was
     held); the operator writes v53_archive/inputs/rule5_list_2027.json and runs, first on a clone named like BF, then
     in BF (A-R9-4 R9b steps 3 and 4). The clone sits in a scratch parent, with BF's parent outputs cloned beside it
     (the manifest check and package.py read ../):
        BFN=GN_v51.9_wk22_2026-09-20; ST="$BF/../v53_staging/v53.1"; C="$ST/r9b.reh/$BFN"; mkdir "$ST/r9b.reh"
        cp -c -pR "$BF" "$C"
        cp -c -pR "$BF"/../GordoNation_Calculator_v53.1* "$BF"/../deploy_manifest_v53.1*.json "$ST/r9b.reh/"
        cp -c -p "$BF/../$BFN.zip" "$BF/../$BFN.zip.pre-v53_1" "$ST/r9b.reh/"
     Then, from "$C" (and afterwards from BF, the same commands and arguments):
        python3 -B update_options.py --rule5 v53_archive/inputs/rule5_list_2027.json --utc <UTC>           dry run
        python3 -B update_options.py --rule5 v53_archive/inputs/rule5_list_2027.json --utc <UTC> --apply
     with <UTC> = <the run's date>T12:00:00Z; then the deploy label (v53.1.<n>), stamp --apply and --check (exit 0),
     verify (on the clone: verify_calc.py --root "$C" --report <outside BF and the clone>; FAIL 0, no RULE5 WARN),
     price_identity_v53.py --digest "$C" (the install digest, unchanged), page_v53/patch_new_v53_1.py --check
     "$C/calc/gn-app.js" (patched), package.py dry then --apply, and the manifest check (23 of 23; copy 3 equal), as in
     section 4. In BF, the changed files must equal the clone's byte for byte. Remove "$ST/r9b.reh" once its logs are
     kept.
  2. R9c, a reviewed pre-opening-day round (hard deadline Fri 5 Mar 2027): GN_DATA_WEEK, verify's G6 and
     pre_installed audits, the season-c fallback texts and the S < 1 ban's input in the engine, W6 on the real
     workbook, and the page items needed before --add-new. Its install writes the build.json key r9c.
  3. The season start, once, before the first refresh (it re-prices nothing):
        python3 -B season_start_v53.py --root . --schedule v53_archive/inputs/hs_schedule_2027_R_f86a8c3e3e7f.json
                --gndaily-start 2027-03-25 --report <outside BF>                                         dry run
        (the same with --apply)
     It archives the 2026 daily feed and options ledger in calc/gn-history.js, starts the 2027 feed and moves
     build.json gndaily_start to 2027-03-25. The first W4 after it rolls the options ledger over to 2027.
  On the opening-day pull (e = 0) W1 refuses; update_calc_weekly.py --g13-live --pull P --report <outside BF> and
  verify_calc.py --opening-day P --report <outside BF> confirm the board still equals v53.0's prices.

  The guards (in code; no price is involved, they only stop a run):
  - THE R9c GUARD (F9). W1 --apply in BF refuses, before any write, until build.json carries r9c:
      REFUSED (exit 2) -- nothing written: this is the live build folder and build.json carries no r9c: no 2027 weekly
      runs in BF until R9c is installed (...)
    Its dry run prints the same text as one WARNING line. Only R9c's reviewed install writes r9c; never add it by hand.
  - THE RULE 5 GUARD (F19). The install carries the 2026 list and names it 2026 (build.json rule5, season 2026). From
    the season start on (options season 2027), update_options.py --apply refuses, so W4 and the rollover stop:
      REFUSED (exit 2) -- nothing written: the Rule 5 list in calc/gn-app.js is 2026's (build.json rule5) and the
      options season is 2027: enter the 2027 list first (C-R6-7 (d); R9b: update_options.py --rule5 ...)
    Its dry run prints it as one WARNING and exits 0. A hand edit of the RULE5 literal or of build.json rule5 refuses
    the same way. Verify then prints one WARN line, "RULE5: the Rule 5 list in calc/gn-app.js is 2026's (build.json
    rule5) and the options season is 2027: enter the 2027 list (R9b; C-R6-7 (d))". What to do: run R9b (step 1). The
    line never appears off season.
  - W1 also refuses before the opener and without a season start; W3 refuses a season-c placement whose texts R9c has
    not written yet (exit 2, a named message) and a declared S < 1 ban; W6 refuses the real workbook.

================================================================================
6. THE CEILING WORKBOOK (unchanged until R9c)

  Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx is not written by the install. It keeps v53.0's install state
  (12497fd2...): its prices equal v53.1's at e = 0, and its banners still say v53.0 and name Methodology v22 until
  R9c. At v53.0's install, 2_Org_Rankings recomputed (River Cats 45,410 still first, KC Gray Hotdogs 43,020 second).
  Until R9c, do not run on BF:
  - resync_ceiling_workbook_v53_0.py without --weekly: the install-layout resync accepts only build v53.0 from v52.0
    and refuses build v53.1;
  - workbook_check_v53.py without arguments: it looks for PLAYERS_2026-10-03_v53.1.json, which does not exist.
  W6 (--weekly) runs on a copy, with --root . --workbook <copy> (section 2).

================================================================================
7. CHECKS AND TESTS: WHERE AND HOW EACH RUNS

  On BF (each alone; reports outside BF):
    python3 -B verify_calc.py                                          FAIL 0 (at the install, WARN only the
                                                                       KEEP INJURY MODULE line)
    python3 -B stamp.py --check                                        exit 0
    python3 -B price_identity_v53.py --digest .                        the install digest, unchanged
    python3 -B test_engine_guards_v53_1.py --root . --stage ../v53_staging/v53.1     alone; 22 PASS, 0 FAIL
    python3 -B rate_engine.py --selftest --root .                      162 passed, 0 failed (reads ../v53_staging/v53.1
                                                                       r8base and gate7b.sc_wk, kept read-only to R9c)
    python3 -B verify_calc.py --selftest ; python3 -B manifest_check_v53.py --selftest
    python3 -B page_v53/patch_new_v53_1.py --check calc/gn-app.js       patched
  Every manifest check passes --manifest ../deploy_manifest_<build>.json explicitly (F3), for a deploy folder:
    python3 -B manifest_check_v53.py --dir ../GordoNation_Calculator_<build> --manifest ../deploy_manifest_<build>.json
  and, after an upload, on the commissioner's network word only:
    python3 -B manifest_check_v53.py --site <the site URL> --network --manifest ../deploy_manifest_<build>.json
  STAGE-only (F17): test_weekly_v53.py, test_rosters_only_v53.py, test_deploy_label_v53_1.py and test_rule5_v53_1.py
  are not installed, because their fixtures are not (a synthetic 2027 pull in BF would be read as the newest pull).
  Each runs only from its tracked deliver copy, on a STAGE tree built from ../v53_staging/v53.1/r9base and the R9
  finals:
    redesign/v53/rounds/R8/deliver_R8c/S2c/test_weekly_v53.py
    redesign/v53/rounds/R8/deliver/S2c/test_rosters_only_v53.py
    redesign/v53/rounds/R9/deliver/S2d/test_deploy_label_v53_1.py
    redesign/v53/rounds/R9/deliver/S4d/test_rule5_v53_1.py
    python3 -B <deliver copy> --root <the STAGE tree> --stage ../v53_staging/v53.1
  test_weekly_v53.py and test_rosters_only_v53.py each run alone (test_rosters_only_v53.py with --workers 3).
  The STAGE tree, built from BF with ST="$BF/../v53_staging/v53.1" and D9="$BF/redesign/v53/rounds/R9/deliver" (a new
  name each time; remove the tree once its logs are kept):
        T="$ST/stest_<YYYY-MM-DD>"; cp -c -pR "$ST/r9base" "$T" && chmod -R u+w "$T"
        for p in S2d S4d S5d S6d S10d S12; do
          (cd "$D9/$p" && shasum -a 256 -c R9_FINAL.sha256 >/dev/null && sed 's/^[0-9a-f]*  //' R9_FINAL.sha256 |
           while IFS= read -r f; do mkdir -p "$T/${f%/*}"; cp -p "$f" "$T/$f"; done) || echo "STOP: $p"
        done
  These six finals lists name tree paths. The other R9 finals are not copied: S7b's belong under S7/, S9's README
  would make a second README in the tree, and M23's script belongs in Reference/. $ST/r9base is kept only until R9
  ends (A-R9-8). After that, start from the R8 gate's tree, which holds the same 454 files plus r8_reports/:
        cp -c -pR "$ST/gate8" "$T" && chmod -R u+w "$T" && rm -rf "$T/r8_reports"
        (cd "$T" && shasum -a 256 -c "$BF/redesign/v53/rounds/R8/runlogs/GATE_R8c/gate8_after_GR8-0.sha256" | grep -v ': OK$')
  The last line prints nothing when the tree is right; then run the loop above. If neither $ST/r9base nor $ST/gate8
  is on disk, ask the orchestrator before running these four tests.

================================================================================
8. RETIRED

  - apply_pace_v51.py, pre_roll_basis_switch.py and resync_ceiling_workbook_v52_0.py: v52 scripts; each refuses a
    rate board. The pace multiplier is 1.00 on every record.
  - test_engine_guards_v53.py (v53.0's): superseded by test_engine_guards_v53_1.py.
  - The R7 stand-ins --standin and --standin-pre: refused with --apply on every schedule.
  - README_v53.0.txt: moved to notes/README_v53.0.txt at the install (the release notes of v53.0 live there).

================================================================================
9. THE RULINGS IN FORCE (redesign/DECISIONS.md)

  - D-2 (b): the newcomer prior is phased out through the season, its weight x (1 - e).
  - D-3: e from the pinned 2027 schedule (no weekly statsapi request); the IL placement date is the first refresh
    that sees the designation, refined by the news date; the evidence rule stays deferred to phase 12, its exposure
    reported weekly; the LMR_c denominator is the prior season's league totals x e.
  - D-4: the offseason roster-only refresh; no repricing; new records unpriced until v53.1 prices them in season.
  - D-6 (b): the 216 S2-lite records keep the ceiling-based start after the 2027 -> 2028 roll.
  - C-R6-7: the options ledger for 2027: (a) no level carries from 2026; (b) a move after the regular season's end is
    an offseason move, never a burn; (c) the Palencia recapture exemption covers its 2026 event only, the Halvorsen
    id alias stays; (d) the 2027 Rule 5 list replaces 2026's after the December 2026 draft (R9b; still open).
  - C-R6-8: designation-only records stay priced from day 0, and a routine 60-day move with no news timeline stays on
    the pooled curve; both counts are reported weekly.
  - C-R6-9: the hitter's playing-time class is the two-window blend by e.
  - C-R6-10: the G17 thresholds acknowledged as declared (g17_thresholds_2027.json, pinned in build.json g17).
  - C-R7-1: the in-season Inspector (display only). C-R7-2: no new rule for returning veterans.
  - C-R8-1: a suspension with games left at season's end counts against the next season.
  - C-R8-2 (b): a new player with no MLB rows is a newcomer for 2027.
  - S7b-R1 (b): the runbook's B4 hand check of every name bridge before B5 (section 12). S7b-R8c-F1: the standby
    replay writes a missing tid on a pickup.

================================================================================
10. KNOWN ISSUES (disclosed; none moves a price at the install)

  - G9, the double-count audit: reported, not blocking (a property of the model).
  - N-1: no level adjustment for players back from injury; the returners are checked as a group after the 2027 season.
  - The expected-share curve: its step and its too-slow fall, the next season of players aged 34 and over projected
    too low, and the long-range term flat beyond its last lag knot. The fix tested under the pre-registered second look
    did not pass, so it is not installed, and these defects carry into 2027. Nothing in the price is adjusted for them;
    a later model change would be tested anew (Methodology v23, 25.10).
  - The Inspector's "A = U / SIGMA" row can show a quotient one unit off in the fourth decimal at a rounding boundary,
    as v53.0 does. Display only.
  - EXP-1 is a synthetic-fixture line of the rehearsal (an options case on a synthetic schedule); it is not expected
    on a real 2027 board.
  - The v52 standby's page keeps the 2026 Rule 5 list after R9b (display only).
  - Declare no S < 1 ban in 2027: no source for its input is ruled, and W3 refuses one until R9c.
  - Until R9c: GN_DATA_WEEK (the page's week label) still follows the 2026 calendar; --add-new is off in BF; the
    workbook keeps v53.0's state (section 6).

================================================================================
11. THE BUILD-TIME RULE (--utc)

  build_v53_0.py accepts only a --utc that starts with --built's date (YYYY-MM-DDTHH:MM:SSZ on the same date); v53.0
  was built with --built 2026-10-03 --utc 2026-10-03T23:59:59Z. Every v53.1 writer that stamps a time takes it from
  --utc on its command line, never the wall clock: the install used --date 2026-10-31 --utc 2026-10-31T12:00:00Z, and
  the deploy label, the page patch and update_options.py --rule5 take --utc the same way.

================================================================================
12. ROLLBACK

  Names (bash; REPO as in v53_archive/RELEASE_v53.1.md section 3, the repository root):
        BF="$REPO/2026/Calculator/GN_v51.9_wk22_2026-09-20"
        TOOL="$BF/redesign/v53/rounds/R9/deliver/S11/install_v53_1.py"
        J="$BF/redesign/v53/rounds/R9/runlogs/RELEASE/install/rel/journal.json"
        APPROVED='Commissioner: "start R9", 31 Oct 2026 (the GO for the v53.1 release; orchestrator ruling R9-1)'
  J is the tracked release journal (it holds no absolute path). APPROVED is the release's approval text exactly, as
  RELEASE section 3 sets it: the tool refuses a journal from an install made with a different --approved. Every run
  takes the release's own arguments (--date 2026-10-31 --utc 2026-10-31T12:00:00Z) and a new, empty --log-dir
  outside BF.

  BEFORE OPENING DAY (window A), in this order (the runbook, $BF/S7/ROLLBACK_RUNBOOK_v53.md, has every command):
  A0  the commissioner decides; the decision and the date go into redesign/DECISIONS.md;
  A1  the operator copies first, before anything is removed: the status record; rosters_only_runs/, options_runs/,
      page_runs/ and the wk*_off* pull folders into ../rollback_ro_<date>/; and $BF/S7 into ../rollback_s7_<date>/
      (from here on the runbook's S7 is that copy, because the tool removes $BF/S7);
  then the tool's dry run, then the rollback itself (<date> the day of the run):
        python3 -B "$TOOL" --rollback --dry-run --journal "$J" --target "$BF" --repo "$REPO" \
            --reference-dir "$REPO/Reference" --log-dir "$BF/../v53_staging/rollback_ld_<date>_dry" \
            --date 2026-10-31 --utc 2026-10-31T12:00:00Z --approved "$APPROVED"
        python3 -B "$TOOL" --rollback [--discard-later-runs] --journal "$J" --target "$BF" --repo "$REPO" \
            --reference-dir "$REPO/Reference" --log-dir "$BF/../v53_staging/rollback_ld_<date>" \
            --date 2026-10-31 --utc 2026-10-31T12:00:00Z --approved "$APPROVED"
       (--discard-later-runs when any later run log exists: A1 has copied them). It returns every install path to
       tag v53.0's bytes, restores the build zip from its .pre-v53_1 backup and proves it; it leaves, and lists, the
       later pull folders, R9b's list and the later deploy outputs, and never touches redesign/;
  then A2-A8 of the runbook (build_v53_0.py --rollback, to v52.0), if the decision is to go back to v52.0.
  After the season start, run the tool's dry run first; if it refuses, stop and ask the orchestrator.

  v53.1 -> v53.0 ALONE, after the upload (a device test fails, or v53.1 must come down before opening day): the tool's
  rollback as above, then the commissioner re-uploads the 23 files of GordoNation_Calculator_v53.0.zip as one commit.
  Stopping at v53.0 is allowed (its prices equal v53.1's at e = 0), but v53.0 cannot run a 2027 weekly: before opening
  day either a fixed v53.1 is installed or window A goes on to v52.0. v53_archive/RELEASE_v53.1.md has the six steps.

  FROM OPENING DAY TO SAT 1 MAY 2027 (window B): the v52 hot standby, by the runbook at $BF/S7. The B4 hand check of
  every name bridge before B5 (S7b-R1 (b)) is in the runbook (written by S7b, F15). After 1 May 2027 the project fixes
  forward.

================================================================================
13. THE INSTALL AND THE UPLOAD

  The install (2026-10-31): the 12 updated scripts, the new scripts and records, the operator's standby set S7/, the
  page patch (page_runs/PAGE_PATCH_1.json) and the label (page_runs/PAGE_PATCH_2.json), the spike re-record
  (v53_archive/spike_report_v53_1.json), build.json's g17, rule5 and v53_1 keys, this README, the stamps, Methodology
  v23 and the v53.1 package (GordoNation_Calculator_v53.1, 23 files, ../deploy_manifest_v53.1.json). The per-file list
  with every sha256 is v53_archive/INSTALL_v53.1.json; v53_archive/RELEASE_v53.1.md describes the release, the
  rollback and the commissioner's upload checklist; v53_archive/device_tests_v53.md is the phone checklist and
  v53_archive/CHECKPOINT_2027-04-26.md the four-week check.
  The upload is the commissioner's: the 23 files of GordoNation_Calculator_v53.1.zip to GitHub Pages as one commit
  (the same 23 names as v53.0; nothing added or removed).

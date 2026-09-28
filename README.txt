GORDO NATION TRADE CALCULATOR — v51.20  THE INSPECTOR AT THE ROLL; THE SEASON ROLL'S REVIEWS CLOSED (2026-09-27)
  Built on v51.19. Same pull and data window: scoringPeriod 173, matchup period 22, Week 22 data.
  Rosters through 2026-09-22 (scoringPeriod 182). No weekly refresh ran. No price or rank moved.
  Service worker: gordo-calc-v93-2026-09-13-v51.20.  GN_BUILD v51.20, GN_DATA_THROUGH 2026-09-13,
  GN_ROSTERS_THROUGH 2026-09-22, GN_INJ_OPENING 2027-03-25.
  RAW_PER_DOLLAR unchanged at 537.96.
  Acceptance: verify_calc.py FAIL 0 (WARN 2, both standing); see section 6.
  Written into calc/ and build.json by build_v51_20.py like v51.19 (backups *.pre-v51_20); package.py made
  GordoNation_Calculator_v51.20/ and its zip (21 files, as v51.19). Methodology v20
  (Reference/Trade_Calculator_Methodology_v20.docx) records it. 394 Inspector panels change (section 2): the 38
  in-season floor chains now print the figures their floor was set on, and 356 panels change a residual row's label
  only. No priced field and no Trade Desk value moves.

================================================================================
1. WHY

  The redesign plan's phase 0 (redesign/PLAN.md) lists what must be done before v52.0 ships. On 27 Sep the
  commissioner ruled that the current engine, REG and g included, runs the 2026 -> 2027 roll as v52.0, and that the
  old engine is frozen after v52.0 except for gate fixes. So the roll and its gates had to be finished now:
  - the adversarial review of season_roll.py after its round-2 fixes and v51.18's carry-scope change (recorded as
    never run). Two separate sessions ran it on 27 Sep, one on the rulings and the steps, the other on the gates and
    edge cases. Together they found 10 material defects and 13 minor ones. An independent verification of this build
    then found one more material gap and nine minor ones (section 3 has each, fixed or listed for a ruling);
  - the Inspector at the roll. On a rolled board 442 Pure chains needed a 'documented adjustment' row, because the
    roll's own Pure step was not in the chain, and 33 recency-floor chains already failed to reconcile (section 2);
  - verify_calc.py's r identity was exact only under --roll. A hand edit of r by 1 passed it (section 6).
  The commissioner's Sitting A answers (27 Sep: "approve the recommendations; D8 is a market incentive") govern the
  redesign (redesign/DECISIONS.md). For this build they mean one thing: D8. The eight relievers who graduate at the
  roll keep the §9 x0.80 inside their Pure. v51.20 leaves that as built, and the Inspector names it on their rolled
  chain as a market incentive. They rule on nothing the roll lists in section 3: those questions are still open.

================================================================================
2. THE INSPECTOR                     gn-app.js (source: inspector_v51_20/gn-inspector-roll.js + build_v51_20.py)

  (a) THE ROLL'S OWN STEP. season_roll.py now stores, on every record, the factors its Pure step multiplied
      (eng.roll, section 3). The page prints them as the chain:
        Pure at the close of 2026  x  age step / growth step / §13.1 carry / completed-season anchor / §19.6 ratchet /
        regression / Father-Time cliff  x  the tier re-read's own factors (a graduate's growth falls away, the
        veteran clock)  =  Pure
      Every figure is one the roll stored (gnRollChain), and verify_calc.py --roll re-derives each of them (section 6).
      A floor keeps its own rows, because its Pure is the larger of two figures and both are shown. A graduate priced
      anew (T3 -> T5 on his MLB career best) keeps his depth chain and a note naming the tier re-read. A chain is used
      only while the record's Pure is still the roll's (eng.roll.pc1) and the roll closed the season before Current;
      after the first 2027 refresh moves a Pure, the record's own basis chain returns (section 7). On the rehearsed
      rolled board (section 5), every chain reconciles in both views with no residual row.
  (b) THE RECENCY FLOORS. An in-season floor (the RECENCY FLOOR v16 note) is shown on the pace it was SET on, from
      its note, where v51.19 used today's pace. It also shows the June 24 vet scarcity, which was applied after the
      floor was set. On v51.19, 33 of the 38 chains did not reconcile: Mike Trout's showed 841 for a Pure of 1,115,
      Max Muncy's 865 for 1,122. Now all 38 do. The other 5 change their printed figures too (their set-on pace): Jake
      Burger, Colin Holderman, Jake Bauers, Gregory Soto, Taylor Clarke. The flow tree's floor box prints its two
      numbers on their own line; the old label was cut at 31 characters once both were four digits.
  (c) THE RESIDUAL ROW. A residual is named only by a factor stored on the record that equals it (to 0.006, the June
      re-pace test). Those factors are the REPACE v20 factor, a recency-floor lift recorded as 'Pure A -> B', and the
      park, speed-aging and closer percentages (gnResidAttr). Anything else is an 'Unattributed residual' in the list
      and '(unattributed)' in the tree. The old row named a cause from any word in the notes: Manny Machado's x1.134
      read 'speed-aging, park factor', two -5% terms that cannot make x1.134; it is his June recency-floor lift,
      724 -> 822. 'MiLB proximity' named six residuals that proximity cannot cause, since §11 moves Hit%, not Pure.
      The tree reads '(rounding)' only for a gap the printed figures' rounding can make: the product of the printed
      chain within max(1.1, 0.5 + 0.1% of Pure) FP of Pure, the checker's strict tolerance. As first built it said
      '(rounding)' for any gap within 1%, which named gaps no rounding makes (the verification: Cole Carrigg's tree
      printed 'FV47 tool ceiling 907' and x1.00 for a Pure of 905); 47 such boxes now read '(unattributed)'.
  CHANGED PANELS ON THIS BOARD (inspector_equiv_v51_20.js; every other panel byte-identical in all four states):
    floor chains (38): Aaron Bummer, Anthony Bender, Antonio Senzatela, Aroldis Chapman, Austin Hedges, Brett
      Sullivan, Brooks Raley, Bryan Reynolds, Bryce Harper, Christian Vazquez, Colin Holderman, Connor Seabold,
      Dominic Smith, Drew Pomeranz, Eduardo Rodriguez, Gregory Soto, Ildemaro Vargas, Jacob deGrom, Jake Bauers,
      Jake Burger, Jameson Taillon, Joc Pederson, Jorge Lopez, Jorge Soler, Jose Altuve, Jose Berrios, Josh Bell,
      Max Muncy, Mike Trout, Nolan Arenado, Ozzie Albies, Richard Lovelady, Ryne Stanek, Taylor Clarke, Tim Mayza,
      Xander Bogaerts, Yimi Garcia, Yu Darvish -- only the list's Pure section and the tree's PURE column differ: the
      pace the floor was set on, the floor, and the June 24 scarcity row.
    residual relabels (356), the label only, the factor unchanged:
      tree 'x adj (proximity)' / '(park)' / '(park,proximity)' / '(C-aging)' -> 'x adj (rounding)'              271
      tree 'x adj (proximity)' -> 'x adj (unattributed)' (a gap rounding cannot make)                          37
      tree 'x adj (rounding)' -> 'x adj (unattributed)' (a gap rounding cannot make)                           10
      list 'Documented adjustment (see audit notes)' -> 'Unattributed residual'; tree '(see notes)' ->
        '(unattributed)'                                                                                        23
      list 'Documented adjustment (see audit notes)' -> 'Recency-floor lift carried in Pure (Pure A -> B)'      8
      list 'Documented adjustment (MiLB proximity)' -> 'Unattributed residual'; tree -> '(unattributed)'          6
      list 'Documented adjustment (speed-aging, park factor)' -> 'Recency-floor lift ...' (Manny Machado)        1
    Residual rows stay 101 in the list (63 June re-pace, 29 unattributed, 9 floor lift) and 591 in the tree (439
    rounding, 76 unattributed, 67 June re-pace, 9 floor lift). Every name, and each panel's from -> to labels, is in
    build_report_v51_20.json (gates.inspector_equiv_v51_20.panels: by_class, detail).
    Nothing changes in values: getValue and fmtValue are identical over 103 settings (218,154 checks), and PLAYERS,
    GNDAILY, OPTIONS_DATA, RULE5 and RAW are byte-identical.

================================================================================
3. THE SEASON ROLL: THE REVIEWS' DEFECTS, AND THE VERIFICATION'S                             season_roll.py

  Fixed in the build (backups *.pre-v51_20; the header's v51.20 section has each one):
  F1  In-season anchors take the COMPLETED season (§19.6: "only the actual banked total is used"; "the ratchet floors
      at the prior full-season peak"). The anchor is round(banked). Pure moves by banked / the stored peak, as the
      weekly re-anchor moves it. A season that fell below the prior full-season peak reverts to that peak and its old
      clock. The roll kept max(peak, ef), a to-date high-water mark the season never finished at.
  F3/D6  update_calc_weekly.py reads the locks season by season (lock_on). The roll's preflight refuses a source
      whose weekly script still reads the notes alone. Otherwise the first 2027 refresh would have re-set
      pm = 2 - 1/F on the 8 imports the roll closed, and retired the pm and blocked the ratchet of all 56 floor
      records for the whole season.
  F4/D5  The post-roll injury re-run instruction is gone. apply_injury_v2.py refuses a rolled board: it is not
      season-aware, and on a rolled copy the review saw it reprice 31 records no ruling covers. A T5 graduate's
      dropped carve-out is marked inj.tool_basis_at_roll (36 on the rehearsed roll).
  F5  eng.roll on every record (section 2).
  D1  S10 re-derives every class's Pure' from the pre-roll board with its own code, the §13.1 carry included. The IL
      days the carry read go to DIR/season_roll_il_days_2026.json with the feed's sha256. verify_calc --roll re-derives
      the carry value and route from the feed.
  D2  verify_calc --roll derives each record's class itself. It re-derives the ratchet on every class, the F1
      anchor, a production graduate's clock and a tool graduate's MLB career best. It requires every anchor line to be
      rebuilt on the closed form, and eng.mid, eng.bd, eid, the roster fields and the audit notes to be kept.
  D3  regular_season_end must be a date in season Y. The rolled build.json drops it and records
      prior_regular_season_end, so a stale date cannot pass the next roll.
  D4  verify_calc --roll FAILs a --fixture roll, an unapplied §19.3 switch, an incomplete season, and a folder whose
      own end gate failed.
  Minors fixed in the build:
  - IL days are read by MLBAM id. The old name map missed every 'Jr.' and hyphenated name, so Ronald Acuna Jr.,
    Bobby Witt Jr. and Vladimir Guerrero Jr. were carried as if never on the IL (see section 4).
  - The carry needs an ESPN-pool record, as banked_total does (Joe Musgrove).
  - avail() takes the pitcher branch only for pitchers.
  - A structural preflight refuses a malformed record by name.
  - A T5 graduate on a shared MLBAM id is refused (latent: the Maxwells, 687209).
  - In a real roll, the injury feed and the MLB season file must post-date regular_season_end.
  - A failed end gate marks DIR (ROLL_FAILED, build.json rolled.verify_roll). The README's acceptance line is stamped
    only after the gate.
  - A vet-basis T3 -> T1 graduate records its retired phase.
  - pre_roll_basis_switch.py stamps the build it ran on.
  AFTER THE BUILD'S INDEPENDENT VERIFICATION (27 Sep; none of these moves a price on this board: the rolled PLAYERS
  of section 5 is byte-identical to the one the build rehearsed):
  D7 (material, the one the verification found): the D7 warning looked only at in-season ratchets. Three more
      veterans carry a June recency-floor lift inside Pure through the roll unflagged, against the 23 Sep ruling of no
      permanent floor after the roll. The June T1 -> T2 audit wrote those floors in lower case ('recency floor Pure
      A->B'), and season_marker('rf') reads only the upper-case v16 note, so the roll treats them as ordinary
      veterans and its step or carry multiplies the lifted Pure. floor_lifted_anchor() now lists every veteran whose
      Pure is more than 0.5% above its peak-derived Pure (peak x scarcity x rm x cliff) with a lift in its notes,
      except a recency-floor class or a carry that took the floor route (both recompute the floor). All four go to
      the commissioner under the one D7 ruling (section 7), each with its rolled figures; nothing is changed.
      Gray, Springer and Machado carry the same kind of lift and are not listed: the carry's floor route won, so
      their floor is recomputed (a what-if confirms their Pure' does not move).
  - verify_calc --roll re-derives every eng.roll row, factor and printed figure from the pre-roll record, in the order
    the roll writes them: the step's clock, REG and cliff; the growth ages and factors; the carry's pace, IL days,
    availability, expectation, multiplier and cap; the anchor's banked total, peaks, revert and prior peak; the
    ratchet's banked total, peak and rm; the tier re-read's rows, from / to and a fresh price's career best. Before,
    only start x the product was held to Pure', so a swapped pair of factors or a wrong printed figure passed every
    gate and would have been shown to the league. On the rehearsed board: 2,985 rows.
  - The tree's '(rounding)' label (section 2 (c)).
  - A panel whose list view has no Pure chain now FAILs verify (inspector_check counted it; nothing read the count).
  - A record's own MLBAM id is never read by name for IL days: the name is for a record with no usable id of its own,
    in season_roll's il_days, S10 and verify --roll. Before, Jose Devers (id 691410) took feed id 672701 by name and
    Yunior Marte (805074) took 628708; both 0 days, so no price moved.
  - The preflight refuses an in-season ratchet whose prior full-season peak is on no record (no eng.pk_prior, no
    ratchet note, not a §19.3 switch). Such a record was anchored on its completed season with no revert test at all,
    and S10 and verify passed it (the reviewers' case: Freddy Peralta with eng.rch set and no ratchet note).
    eng.pk_prior = {pk, py} settles it (pk null when it passed no full-season peak). On today's board none is refused.
  - The structural preflight refuses a PV-blended record without its blend fields, and verify_calc names a PV block
    missing a field instead of raising KeyError (a --fixture roll and verify both used to crash on one).
  - A third question for a ruling is listed by the roll (CAP, section 7): the carry won, capped at the career peak
    from BEFORE the ratchet the same roll fired and recorded.
  - Every pending record in the roll's report and README carries its figures as the roll leaves it.
  Deferred, each because it moves a price and needs the commissioner's ruling (section 7): D7 (4 records), F2 (4),
  CAP (3), the carry's Pure < 300 short-circuit (18) and its scarcity cap (13). The roll prints D7 as a WARN each and
  lists D7, F2 and CAP in its report and its README section 6.
  Not fixed, listed in section 7: on the live board the Inspector gate cannot catch a chain that stops reconciling
  outside the 38 floors (a residual row absorbs it), and a rolled record's chain after the first 2027 Pure move.

================================================================================
4. WHAT THE FIXES DO TO THE ROLL (dry runs of season_roll.py.pre-v51_20 and season_roll.py on the same copies)

  On the switched board of section 5: 26 records' rolled RA moves, net RA -375 (RAW' 502.84 -> 502.93); Payton Tolle's
  Pure also differs by 0.1 of rounding, with his RA unchanged. On the unswitched v51.19 board (--fixture): the same
  26, net RA -375 (RAW' 501.59 -> 501.69). The final data will differ. The 26:
  - F1, 22 in-season anchors on the completed season. 3 revert to the prior peak: Matt Gage (192, 2025), Brandon
    Lockridge (156, 2025), Chuckie Robinson (19, 2021). Kyle Harrison RA 1,128 -> 1,051, Sean Burke 1,183 -> 1,144,
    Foster Griffin 1,014 -> 991. Cesar Prieto's completed 2026 total is 0 FP, so his import anchor goes to Pure 0
    (RA 182 -> 0).
  - The IL-day id fix, 3 carries: Acuna Jr. RA 1,278 -> 1,334, Witt Jr. 1,310 -> 1,341, Guerrero Jr. 1,113 -> 1,138.
  - Joe Musgrove leaves the carry (off the ESPN pool): 231 -> 224.
  These are the rules as written, not new rulings. The commissioner's OK on v52.0 covers them. The verification's
  fixes move none of them and nothing else.

================================================================================
5. THE REHEARSAL (scratch copies of this build; regular_season_end set in the copy only)

  The real final data is not in yet: no final ESPN pull, no final weekly refresh. The rehearsal therefore runs the
  pre-roll order on a mirror of this folder with the v51.19 board (data through 2026-09-13). regular_season_end was
  set to 2026-09-13 in the copy only (step 3's statsapi re-pull was not needed: the season file was built 2026-09-15).
  With the real end, 2026-09-27, the real roll REFUSES, as it must, on 3 checks with nothing written: the data, the
  injury feed and the MLB season file all predate the season end.
   2. apply_injury_v2.py --apply: INVARIANTS ALL CLEAR, RAW 537.96 -> 537.97.
   4. pre_roll_basis_switch.py: 11 switched (stamped v51.20), RAW 537.97 -> 539.43.   5. promoted.
   6. apply_injury_v2.py --apply: RAW 539.43 -> 539.43.   7. README card restamped to 537.96 -> 537.97 -> 539.43.
   8. verify_calc.py: FAIL 0 WARN 2. Inspector: 2,118 panels, 0 chains not reconciling (list and tree).
   9. season_roll.py (real, --apply --confirm-season-complete): preflight PASS; weekly refresh season-aware.
      - Carry 458: 425 carry, 17 ratchet, 16 floor; 256 marked down, 178 up, 45 capped at the career peak.
      - Ratchet fired 30, won 27.
      - Tier moves: T3 -> T1 production 59, T3 -> T5 tool 36, T3 -> T1 veteran 4, T1 -> T2 2.
      - In-season anchors 232: 19 moved to the completed season, 3 reverted.
      - RA 842,515 -> 790,695, RAW 539.43 -> 502.93 (pool 1,394).
      - S10 ALL CLEAR.
      - WARN D7 x4: Ketel Marte, Jose Ramirez, Michael Wacha, Matt Chapman. F2 listed (4). CAP listed (3).
  10. verify_calc.py --roll: FAIL 0 WARN 2 (the roll ran it as its end gate, then it was run again by hand; the README
      acceptance line was stamped from that verdict). It re-derived 2,118 classes, 458 carry values, 232 anchors, 59
      graduate clocks, 36 career bests and 2,985 eng.roll rows.
  THE INSPECTOR ON THE ROLLED BOARD: 2,118 panels in both views, 0 render errors, 0 undefined/NaN, 0 chains not
  reconciling, and 0 residual rows in the list and 0 in the tree.
  - 2,034 chains are the roll's own step.
  - 36 are graduates priced anew (depth chain plus a note).
  - 48 are floors (their own rows).
  The v51.19 roll needed 442 'documented adjustment' rows on such a board.
  Two more rehearsals on fresh mirrors of the finished build gave byte-identical rolled folders (all 28 files). The
  rolled PLAYERS (sha256 fba70c45d982cbe9...) is also the one the build rehearsed before the verification's fixes.
  NEGATIVE CHECKS (all on scratch copies):
  - regular_season_end 2026-09-27: REFUSED, 3 checks. 2025-09-28 and 'TBD': REFUSED. Nothing written.
  - A --fixture roll is not promotable. verify_calc --roll FAILs it 6 ways on the unswitched board and 5 on the
    switched one: fixture (build.json and the report), its own failed gate (ROLL_FAILED, build.json and the report),
    and on the unswitched board the switch not applied.
  - r + 1 on one record: verify FAIL 1, live and rolled.
  - The rolled board promoted over a copy of this folder: apply_injury_v2.py REFUSED; update_calc_weekly.py REFUSED
    (build.json season 2027 is not GNDAILY_START's year); verify_calc.py FAIL 0 WARN 2 with 0 residual rows.
  - Weekly locks on the rolled board: the notes alone give floor 56 and import 8; lock_on gives 0 and 0; eng.rch 0.
  - The reviewers' edge cases (their em.py, 26 cases, each as a real and a --fixture roll): every corrupted record is
    refused by name, including now a PV record without eng.pv.w_ceil (it raised KeyError before) and an in-season
    ratchet with no prior peak on record (it rolled silently before); Zachary Maxwell graduating on the shared id
    687209 is refused; no run ends in a traceback.
  The reviewers' 38 output mutations (their vm.py, on this rehearsal): verify --roll catches all 38, baseline FAIL 0.
  The reviewers' code mutations of season_roll.py (their cm.py: the 26, the build's 4 new ones, and one more for the
  verification's IL rule; the id-keyed IL mutation re-anchored on the new line), each run as a real roll, 31 in all:
  - 18 are stopped by S10 and 7 by the end gate (verify --roll), 2 are refused before anything is written (a GP_ and
    a REG typo).
  - 4 move no record on this board (0 records' r moved): the ratchet's +0.5 margin, T4 over 30, a graduate's growth
    when g(a') = 1, and an own id the feed lacks falling back to the name.
  - The id-keyed IL lookup, which moved no record either, is now caught by the per-row check: by name only, Will
    Smith (two in the feed) prints no IL days where the feed has 82.
  The verification's own poisons of the rolled board (its vpoison.py): the 7 that passed with FAIL 0 now FAIL -- Ketel
  Marte's step and carry factors swapped (product unchanged); his carry's pace, IL days, availability and expectation;
  his step's clock and REG; Brooks Lee's anchor banked total and peaks; Matt Gage's prior peak; Kumar Rocker's tier
  clock and 'T9'; Dalton Rushing's career best. Grant Taylor's live eng.pk x1.2 still passes (section 7).

================================================================================
6. GATES

  build_v51_20.py   guard: calc/ is the packaged v51.19 (folder and zip agree), PLAYERS ==
                    PLAYERS_2026-09-26_v51.18.json, the identities exact, the roll's age audit reproduces build.json.
                    Then 9 Inspector patches, each matched once and none in PLAYERS, the literals byte-identical, and
                    the two node gates. --reapply reproduces calc/, build.json and the report byte for byte.
    inspector_equiv_v51_20.js   packaged v51.19 vs the candidate, alone and on the full page stack: values identical,
                    and panels identical except the floor chains and residual relabels (a change of any other
                    kind FAILS): 394 = 38 + 356, other 0, in all four states.
    inspector_check_v51_20.js   both views: render errors 0, undefined/NaN 0, no list chain 0, chains not
                    reconciling list 33 -> 0 and tree 33 -> 0.
  verify_calc.py    FAIL 0, WARN 2 (the 23 designation-vs-module lags and the 9 T3s on a veteran basis, both
                    standing). New in v51.20:
                    - the r identity is exact in both modes (the tolerance of 1 is gone);
                    - THE INSPECTOR GATE: inspector_check_v51_20.js on calc/gn-app.js. Every Pure chain must
                      reconcile in both views, every panel must have a list chain, with no render error or
                      undefined/NaN. Under --roll no chain may carry a residual row. The v51.19 page FAILS it (33 + 33).
                    - the pace-gate exemptions are season-scoped, as the roll and the page read them;
                    - a PV block missing a field is named (a FAIL), not a traceback;
                    - --roll: section 3's D1, D2 and D4, and every eng.roll row and printed figure re-derived.
  package.py        GordoNation_Calculator_v51.20/ and its zip equal calc/'s 21 deploy files byte for byte (CRC OK,
                    stamps v51.20 / 2026-09-13 / 537.96 read back from the archive); the build zip (518 entries) passes
                    the same checks, and carries 22 raw Savant CSVs under statcast/data/, as v51.19's did (not the
                    deploy; whether the reproduction archive keeps them is the commissioner's call).
  (no workbook re-sync: every input resync_ceiling_workbook_v51.18.py reads a value from is byte-identical to v51.19
  -- the PLAYERS, GNDAILY, OPTIONS_DATA and RULE5 literals, RAW_PER_DOLLAR, the data, rosters and injury-opening
  dates, and the build.json keys it reads (data window, pull, injury module, gnfv, attrition, time discount,
  statcast); only the identity moved (build, built, GN_BUILD). All 1,412 rows of 1_Player_Inputs match the v51.20
  board on Risk-Adj and $Value, and 2_Org_Rankings stands: River Cats 54,334, KC Gray Hotdogs 50,802, Kansas Sunflower
  Seeds 48,073. The workbook still reads "calculator v51.18" and Methodology v18; its next re-sync runs v51.18 -> that
  build.)

================================================================================
7. STILL OPEN

  FOR THE COMMISSIONER (each moves a price; the roll lists each and applies none):
  * D7 -- four veterans whose Pure still carries a June recency-floor lift that the roll's step multiplies into 2027,
    against the 23 Sep ruling (a floor recomputed once at the roll, none afterwards). RA before -> as rolled -> if
    recomputed as a floor (a scratch what-if of the ruled recompute: the lower-case floor read as a floor, and Wacha's
    anchor on his peak-derived Pure):
      Ketel Marte     Pure 1,331 = 1.321 x the peak-derived 1,007.9; carry      RA 1,227 -> 1,022 -> 954
      Jose Ramirez    Pure 1,235 = 1.216 x 1,015.3;                   carry      RA 1,085 ->   921 -> 790
      Michael Wacha   Pure 1,960.5 = 1.631 x 1,202.0; in-season anchor (3c multiplied the lift into his new peak)
                                                                                 RA 1,725 -> 1,583 -> 971
      Matt Chapman    Pure 973 = 1.440 x 675.9;       age step (IL finisher)     RA   842 ->   758 -> 527
    Net RA -1,042 if all four were recomputed (RAW' 502.93 -> 502.18). Gray, Springer and Machado carry the same kind
    of lift but roll through the floor route, and do not move in the what-if.
  * F2 -- the ruled floor is never tested for a T1 / T2 who finished on an IL designation. Four would rise: Rafael
    Devers Pure' 1,081.6 vs floor 1,217.2, Dansby Swanson 831.8 vs 893.4, Kirby Yates 175.2 vs 311.1, Taylor Walls
    463.9 vs 543.1.
  * CAP -- when the ratchet fires but the carry wins, the carry is capped at the career peak from before the ratchet,
    beside the new peak the same roll records (the Inspector then prints 'capped at the raw career peak 769' beside
    'peak 808 FP (2026)'): Jose Soriano capped at 1,090 vs new peak 1,119 (uncapped 1,151.9), Trevor Megill 769 vs 808
    (813.7), Jake Mangum 595 vs 623 (624.5). Predates v51.20.
  * The §13.1 carry ignores §13's Pure < 300 short-circuit (18 records), and its cap compares a Pure that includes
    scarcity with a raw peak (13 C / 2B / 3B veterans; v51.11's verbatim rule).
  GATE LIMITS, not fixed here:
  * On the live board the Inspector gate cannot catch a chain that stops reconciling outside the 38 floors: the page
    adds a residual row that absorbs the gap. Grant Taylor's eng.pk x1.2 (Pure untouched) passes FAIL 0 and adds one
    unattributed residual (list 101 -> 102). A baseline of the live residual rows in build.json, with a WARN or FAIL on
    a new one, would close it, but every weekly refresh would then need a re-baselining step. On a rolled board no
    residual row is allowed at all.
  * A rolled record's chain lasts while its Pure is eng.roll.pc1. Once a 2027 refresh moves a Pure (a 3c re-anchor or
    ratchet), the basis chain returns and cannot explain the carry or anchor folded into Pure: with the roll chain
    switched off, the rehearsed board shows 440 list and 890 tree residual rows, 396 of them 'Unattributed residual'.
    The fix would append the refresh's factor to eng.roll (update_calc_weekly.py and gnRollChain). It only matters if
    the redesign is not installed before the first 2027 refresh.
  BEFORE THE REAL ROLL:
  * The final weekly refresh and the injury module's post-season feed (steps 1-2), the real regular_season_end, and
    the statsapi re-pull of step 3: no script in this folder writes backtest/gn_backtest_seasons_2023-2026.json (it
    was pulled on 15 Sep from statsapi /api/v1/stats?stats=season with /api/v1/sports/1/players; see its 'source').
  * Before the first 2027 weekly refresh: move GNDAILY_START to the 2027 opening day. The weekly script refuses until
    then.
  Carried from v51.19 (notes/README_v51.19.txt), unchanged unless said:
  * Ruling D-b: nine T1s below peak age by birth date, held T1.
  * The §4 resolver's sole-MLB-line extension (Carlos Rodriguez).
  * The injury re-run after the age fix: Suarez 624 -> 589, Steele 807 -> 851, at the pre-roll re-run (step 6).
  * Duplicate MLBAM ids: 687209 (the Maxwells). The roll now refuses to price a T5 graduate on it (latent until
    2028).
  * McKenzie / Garrett, REPACE v20 in four Pures, the 9 T3s on a veteran basis (4 graduate at the roll).
  * The scoring map: the pending IP1 / SV12 / HR6 / no-fielding map is the league's decision.
  * The roll's tier re-read cannot move a tool T3 with neither eng.aod nor eng.bd (Harris, Thornton).
  * 45 records have no birth date from any source.
  * MLB's terms of use §1(xi) (now also the statsapi re-pull); real iPhone / Android tests; the live GoatCounter count;
    the 2025-line fetch; the first-use cost of a prospect; Savant data outside the deploy; Compare's checks outside
    this folder.
  Closed by v51.20: the Inspector at the roll; the 33 floor chains; verify's r identity; the adversarial review of
  season_roll.py; graduation maturation (D8, ruled: a market incentive, the eight left as built); 'how pace
  multipliers reopen in 2027' as far as the locks go.
  README_v51.19.txt was moved to notes/ with a plain mv: git shows a delete and an untracked file, so stage both.

RUN ORDER TO REPRODUCE
  mv README_v51.19.txt notes/
  python3 build_v51_20.py --apply            # calc/ (backups *.pre-v51_20), build.json, report; copies this README
                                             # to calc/README.txt (--reapply: back to v51.19 from the backups, then apply)
  (no workbook re-sync: nothing it reads moved -- section 6)
  python3 ../../../Reference/patch_methodology_v20.py --apply     # Methodology v20 (no PDF)
  python3 verify_calc.py
  python3 package.py --apply

PRE-ROLL RUN ORDER (build.json pre_roll.order; v51.18's order plus v51.20's statsapi re-pull in step 3. season_roll.py
refuses a real roll that skips the switch, a regular_season_end outside the season, or an injury feed or MLB season
file older than it)
   1. The final weekly refresh (update_calc_weekly.py and its run order), on the final 2026 data.
   2. The injury module's post-season feed (injury_v2_data_<date>.json, named in build.json), then
        python3 apply_injury_v2.py --apply
   3. build.json regular_season_end, from the final 2026 schedule. Then re-pull the statsapi MLB season file after
      that day: backtest/gn_backtest_seasons_2023-2026.json (its 'built' must follow regular_season_end) and
      backtest/gn_backtest_fielding.json, which a T5 graduate's career best and Hit% reliability read; record the
      sha256 (PLAN phase 0, step 3).
   4. python3 pre_roll_basis_switch.py . --out DIR --report DIR/switch_report.json     (DIR outside this folder)
   5. Promote:  cp DIR/gn-app.js calc/gn-app.js
   6. python3 apply_injury_v2.py --apply     (the switched records lose the tool carve-out; RAW moves)
   7. Restamp the README card: its RAW_PER_DOLLAR line must end at build.json raw_per_dollar
      (e.g. '538.06 -> 537.96 -> 539.43.'); then cp README_<build>.txt calc/README.txt
   8. python3 verify_calc.py                 (FAIL 0)
   9. python3 season_roll.py . --out ROLLDIR, then with --apply --confirm-season-complete   (ROLLDIR outside)
  10. python3 verify_calc.py --roll ROLLDIR  (FAIL 0)
  11. The commissioner's OK, with rulings on D7, F2 and CAP (section 7) or an explicit 'as rolled'.
  12. Promote ROLLDIR to calc/ and package v52.0.

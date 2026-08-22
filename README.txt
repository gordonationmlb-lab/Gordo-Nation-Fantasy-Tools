FULL BUG SWEEP (2026-08-22 — v50.4)
  Commissioner-requested end-to-end audit. Three reviewers read all 2,675 code lines;
  every valuation path was executed for all 2,123 players x 480 slider/mode combos; all
  six embedded data blocks were cross-checked against the code that consumes them.
  NINE DEFECTS FOUND AND FIXED (index + mobile, same patch):
  1. [HIGH] EKG dollar scale: the Manager EKG divided by GNDAILY.raw (637.32) instead of
     RAW_PER_DOLLAR (467.65), reading ~27% low vs the adjacent manager bars (River Cats
     $71.8 vs $97.8) and mixing scales with the flat p.d fallback (217 player-days).
     Recomputing at 467.65 reproduces the bar totals exactly.
  2. [HIGH, data] Stale vet trajectories: weekly refreshes reprice r but never rebuilt
     trajectories — 153 of 807 T1/T2 vets had tj anchored to an old r (scales 0.51-1.88;
     worst: Zac Gallen r=1134 showing 574 in year 2 — trajectory built when r was 604;
     also Eovaldi, Springer, Sean Murphy, Treinen among rostered). tj is now re-anchored
     to current r at load, and the pure track tjp is rebuilt from tj and today's Hit%
     wherever it disagrees (another 53 vets carried a stale-h pure track that skewed
     Pure-blend multi-year views). Affects every multi-year and single-year view.
  3. [MED] Fade-on cumulative dip: with bust risk OFF, moving the years slider 1 -> 2
     DROPPED 383 prospects' values, because the multi-year floors still used the unlifted
     RA. All floors (cumulative, single-season, pre-arrival option value) now use the same
     lifted 1-yr value via a shared liftedRA(); the years slider can never show less at
     year N than at year 1. All v50.3 headline numbers unchanged.
  4. [MED] Injury-risk chart legend was BLANK on first paint: the legend filter read the
     chartInjuryRisk global before Chart.js finished constructing (verified against the
     exact chart.umd 4.5.0 the page loads). It now uses the filter's own chartData.
  5. [MED] ROS '26 mode overpriced no-data free agents: an FA with no 2026 form data was
     imputed form = k x r, landing at the ~98th percentile of real forms — Ryan Pepiot
     (no 2026 data) projected 443, above EVERY rostered SP (best actual: Cease 415).
     Imputed form is now capped at the class median, so "no data" can no longer beat
     "good data". FAs with real form are untouched.
  6. [LOW] ROS mode's manager chart y-axis claimed "Total RA" while plotting ROS FP
     (~4x smaller scale); now labeled "Total ROS '26 FP".
  7. [LOW] The Options Tracker search dropdown never closed on outside clicks (its twin,
     the Inspector dropdown, did) and sat over the filter buttons; now closes.
  8. [LOW] Installed (PWA) copies showed permanently blank charts offline because the
     service worker refused to cache the cross-origin Chart.js bundle while the install
     tip promised offline use; the CDN bundle is now cached after first online load.
  9. [LOW] Single-season pre-arrival years now use the same lifted floor as year 1
     (consistency companion to #3).
  CHECKED AND CLEAN (verified by execution, no action needed): identity r = pc x pm x h
  (0 violations, 2,123 players); d = r/467.65 exact for all; tj = tjp x h; option-tracker
  counts 178/26/0/14 match the data and remaining = max(0, 2 - burns) for all 477; every
  OPTIONS_DATA and RULE5 key resolves in PLAYERS; all 14 Rule 5 compliance chips evaluate
  correctly (roster-level parity 0 violations); deadline-banner date math correct for
  America/Chicago through all three states (countdown -> processing -> closed); Chart.js
  SRI hash matches the 4.5.0 tarball; no duplicate HTML ids, player names, or eids; RLE
  roster decode agrees with p.l for every non-FA; all 569 shape arrays are 145 days;
  GNDAILY day indexing consistent end-to-end; verdict bands and localStorage restores
  sound; "fade-on exceeds tool ceiling" cases all explained by park/pace factors that
  legitimately live in the Pure chain (by design, verified).
  KNOWN QUIRKS LEFT ALONE (documented, not bugs): in ROS mode the Career/2026 line charts
  still plot RA/$ (now correctly labeled); valueAtSnapshot/gnDailyDollars/gnWindow are
  currently unreferenced legacy paths (kept consistent anyway); charts require one online
  load before they work offline.
  29/29 assertions + 8/8 rehydration regression pass on both files.
  Service worker: gordo-calc-v58-2026-08-22 (auto-refreshes installed copies).

BUST-OFF 1-YEAR LIFT SCOPED TO SCOUTING BUST (2026-08-21, third same-day update — v50.3)
  THE BUG (commissioner-reported): Jackson Holliday dropped into a trade slot showed his
  PURE value (1,428) with the RA/Pure blend slider hard left at 100% RA. Cause: the v50.1
  rule for "bust risk OFF at 1 year" lifted straight to the stored Pure — but Pure sits
  above RA for three different reasons (scouting bust in Hit%, the pace multiplier, and
  durability/IL), and the toggle was erasing all three. Holliday is a T3/Established
  production player: his Hit% carries ZERO scouting bust ("bust retired"), and his whole
  RA-Pure gap is pace x0.5 plus a small durability haircut. Every T3/T4 in the universe
  (1,109 players) was over-lifted the same way whenever bust risk was off — worst cases
  all Established prod T3s: Skenes printed 2,242 instead of 1,474, Holliday 1,428 for 671,
  Jared Jones 1,289 for 577, Volpe 1,261 for 593, Woo 2,017 for 1,367.
  THE FIX (index + mobile): a new bustFreeHit() computes Hit% with only the scouting-bust
  layer removed — production basis has none (Established/Honeymoon: no lift; Book: the
  "league adjusts" x0.85 confidence haircut lifts); tool basis removes matrix bust + level
  proximity (T4) or the phase-adjusted effective bust (T3 tool), capped at the healthy
  base. The 1-year bust-off value is now RA x (bustFreeHit / Hit%), further capped at
  max(Pure, RA) so a hot-pace player never prints above the slider's Pure end. Pace,
  durability history, and current-IL stay priced — they are observed, not scouting risk.
  The blend slider owns the RA<->Pure axis again.
  RESULTING 1-YR BUST-OFF PRICES: Holliday/Skenes/Volpe and all Established prod T3s =
  their RA (toggle inert, correctly); De Vries 649 (was 675), Seth Hernandez 469 (was
  498), Snelling 768 (was 817), Kade Anderson 580 (was 617); Book-phase examples: Povich
  213->251, Brady House 329->572. Multi-year fade math untouched (Kade yr-7 single still
  511/1,686). 24/24 assertions + 8/8 rehydration regression pass on both files.
  Service worker: gordo-calc-v57-2026-08-21 (auto-refreshes installed copies).

TRADE-SLOT REHYDRATION (2026-08-21, second same-day update — v50.2)
  THE BUG (commissioner-reported): Kade Anderson in a trade slot with bust risk OFF and the
  slider on year 7 priced at 511 while his 10-year trajectory table showed 1,686 for the same
  year. The trade columns and the inspector were reading two different Kades: picked players
  are saved to the browser's trade state as full JSON snapshots, so a slot re-loaded after a
  page refresh holds the player AS OF THE DAY HE WAS ADDED. A snapshot taken before the
  v50.1 tier restore still carries the ESPN team id in its tier field (Kade: t=9), so the
  bust-off fade gate never opened on the trade side — it printed the risk-adjusted tj[6]=511
  — while the inspector always looks up the live, repaired player and faded him to
  617/0.86/0.4 x 0.94 = 1,686. The same staleness also served old r/pc/tj numbers for any
  player added before a weekly data refresh.
  THE FIX (index + mobile): on load, saved trade slots are rehydrated to the LIVE player
  objects — matched by ESPN id, then name+org, then name; a player no longer in the
  valuation universe is kept as saved rather than silently dropped. Slots now always price
  from current data and current tiers. Verified: stale pre-restore snapshot reproduces 511;
  after rehydration the same slot prices 1,686 (yr-7 single, bust off), 6,725 (yr-7
  cumulative, bust off), and 511 with bust ON — trade side and trajectory table now agree.
  8/8 rehydration assertions + 17/17 v50.1 regression assertions pass on both files.
  Service worker: gordo-calc-v56-2026-08-21 (auto-refreshes installed copies; players
  already sitting in a trade re-price on the next page load).

TIER RESTORE + BUST-OFF REPAIR (2026-08-21)
  THE BUG (commissioner-reported): "Bust risk OFF" never moved a rostered T4's number, and
  search chips showed tiers that don't exist ("T9"). One root cause: roster-sync ingest has
  been writing the ESPN TEAM ID into the tier field `t` for every rostered player (present
  since at least v45). The 16 ESPN teams are 8 orgs x 2 rosters — MLB clubs 1 C-Town /
  2 Gray Hotdogs / 3 Dirty Spikes / 4 High Cheddar / 7 Balking Dead / 8 Sunflower Seeds /
  10 River Cats / 14 MidwestBears, AAA affiliates 5/6/11/9/12/13/15/17 respectively — so a
  "T9" chip was a High Cheddar AAA stash rendered through the chips' 'T'+t concat (the same
  concat printed free agents as "TT4"). Downstream, the bust-off fade gates on t==='T3'/'T4',
  so NO rostered player ever faded: all 57 rostered tool-basis prospects (incl. De Vries,
  Hagen Smith, Seth Hernandez, Sloan, Rushing) sat at full risk discount in every view.
  THE FIX (index + mobile, same patch):
  1) TIER RESTORE at load: the ESPN id moves to a new field p.tid; the true tier is recovered
     from the notes' "ENGINE ...: Tn" tag (406 of 428) or the engine basis (tool->T4,
     prod->T3, depth->T5; 22 players, unambiguous). Restored distribution: T1 213 / T2 74 /
     T3 117 / T4 19 / T5 5; zero non-T1..T5 tiers remain. Chips render the tier directly
     ("T4", not "TT4"/"T9"). The fade gate, inspector type row + formula sections, T3 phase
     logic, and career-arc decay/onset all see real tiers again.
  2) THE 1-YEAR (default) VIEW now answers the switch. It had never consulted FADE_MODE —
     it read stored RA/Pure, which carry the whole stack (ceiling x maturation 0.3-0.8 by
     level x Hit%), so the toggle was a no-op on the headline number. Bust-risk OFF at 1
     year now lifts the bust/Hit% layer only: value shows Pure; maturation and the level
     discount stay on. Multi-year views unchanged — the fade still phases bust + SP/RP
     blend + maturation out by peak age (26 H / 27 P). Verified: De Vries 506 -> 675 (1yr)
     and 4,443 -> 10,378 (10yr cum); vets unmoved (Trout 746/746 and 4,044/4,044).
  3) STALE BLEND-NOTE OVERSHOOT: prospectBlend()'s notes-regex fallback divided out an
     "SP/RP/Washout blend" the v29 grade rebuild had already removed from the ceiling chain
     (pc = tc x matur, verified) — with fade ON the 3 players still carrying the note
     overshot 2-4x (Sykora's best year printed 2,694 against a 1,548 tool ceiling; now
     1,455). Fallback removed; eng.bdisc (89 players, verified pc = tc x matur x bdisc)
     is the only blend still divided out.
  34/34 harness assertions pass on both files. Service worker: gordo-calc-v55-2026-08-21
  (auto-refreshes installed copies).

RULE 5 SELECTOR ADDED (2026-08-18, second same-day update)
  NEW: a fourth Options Tracker button — RULE 5 DRAFT (14) — listing the July 14, 2026 Rule 5 class
  (verified against the transaction log: 14 cross-org AAA->MLB processed moves that day). Each row shows
  position, drafting club, original club, and a LIVE compliance chip: green "ON MLB ROSTER" when the pick
  is where the rule requires him; red flags for an illegal demotion (original club may recapture) or a
  waiver drop (original club may claim). Opening any pick's record shows a navy RULE 5 badge and the
  restriction: a Rule 5 selection may NOT be demoted from the MLB roster regardless of remaining options —
  he leaves that roster only via original-manager recapture on an illegal demotion, or off waivers after a
  drop by the drafting manager. All 14 picks are currently compliant. The class: Headrick, Tolle,
  Holderman, Palencia, Harrison, Messick, Dingler, Blubaugh, Aranda, Garcia Jr., Diaz, Tucker, Pagan,
  Buxton. Service worker: gordo-calc-v54-2026-08-18.

GORDO NATION TRADE CALCULATOR — OPTIONS TRACKER HOTFIX + FILTER BUTTONS (2026-08-18, same day as wk19)
  THE BUG (commissioner-reported): Noah Schultz showed options burned May 27 AND May 28 — physically
  impossible (a burn happens when the player hits the AAA roster; the earliest a second burn could follow
  is ~4 days later). A full audit against the season ESPN transaction log found THREE ingest defects:
    1) ESPN double-logs processed moves on consecutive days (306 duplicate mt-244 rows, 17 mt-245);
       every duplicate was counted — 48 players showed >2 burns (up to 5). Schultz's May 28 was one.
    2) ESPN drop rows carry the dropping team in the *to* column; the old ingest classified add-vs-drop
       by which side looked like FA, so ~244 drops were written into the ledger as "Added by ..." events —
       and some were charged as rule-(b)(3) burns. Drops NEVER burn (Rulebook VI(b)).
    3) Rows whose from-column is the literal string "None" were silently skipped, so real FA adds/drops
       vanished — genuine (b)(3) burns were MISSED.
  THE FIX: OPTIONS_DATA fully REBUILT from the raw transaction log (message-type classification, <=3-day
  duplicate-row dedupe, preseason rows set roster level but never burn). The 18 Week-19 reconciliation
  events (Aug 10-16) and the Aug 10 Hicks-Jensen trade events are preserved on top. Result: 477 players
  tracked (was 468), burns 0:273 / 1:178 / 2:26, ZERO players over the limit, zero impossible transitions,
  and every count now reproduces from the log. 191 players' burn counts changed. Recovered missed burns:
  Willi Castro (Aug 6), MacKenzie Gore (Aug 4), JoJo Romero (Jun 27), Casey Mize, Christian Vazquez,
  Keibert Ruiz, Luke Raley, Matthew Boyd, Sean Newcomb, TJ Rumfield. Bryan Woo stays 2-burned / OUT
  (as printed in Issue 19); Noah Schultz is 2 (May 27 + Aug 10-16) — also out; Landen Roupp likewise.
  NEW FEATURE: three filter buttons atop the Options Tracker — 1 OPTION BURNED (178) / 2 OPTIONS
  BURNED (26) / NON-COMPLIANT >2 (0) — with live counts. Tap a button to list the players (club,
  burned/left, most recent burn date); tap a player to open their full record. The non-compliant view
  shows an ALL CLEAR banner while the league is compliant.
  Service worker: gordo-calc-v53-2026-08-18 (auto-refreshes installed copies).

GORDO NATION TRADE CALCULATOR — WEEK 19 REFRESH (2026-08-18)
  Data through Aug 16 (SP145, MP19 complete). GNDAILY 138->145 (569 shapes: 403 rebuilt, 4 new, 162 padded).
  Value refresh: Aug absorption 80%, F=1.295 (~125.1 team games), RAW_PER_DOLLAR=467.65. Identity r=pc*pm*h: 0 violations.
  Pace: 1125 updates; pm recomputed for 562 pace-active players (+4 import-pace at 2-1/F=1.228); 659 repriced.
  Roster sync: 48 org/level changes, 4 drops to FA, 5 rostered stashes bridged to the valuation universe for the
  first time (Valencia, Baez, Lombard Jr., De Paula + NEW entry "Max Muncy (Ath)" — placeholder valuation, LOW conf,
  flagged for the next scouting regrade). Injury sync: 236 designation/ir changes (incl. healing stale flags left by
  earlier passes; their pace multipliers re-engaged per Sec 13).
  Durability: 28 news-feed IL events (Aug 11-17) absorbed; 19 players' files moved (statsapi spine re-harvest pending
  next authenticated browser session — news-feed events are placements/transfers only, same per-spell weights).
  GNROS: 386 forms refreshed (last-30 window via cum-curve recovery; endpoints exact), 474 roles re-fed
  (30-day [SV,HD,BS] window slid one week: 23/30 carryover + exact Aug 10-16 delta), rn 0.7255->0.7340. hz/coef unchanged.
  HISTORY snapshot #12 (2026-08-17, compact). Options: 20 events re-fed, burns: Noah Schultz, Bryan Woo, Landen Roupp, Tyron Guerrero, Brandyn Garcia, Braxton Ashcraft. Week 19 trade
  (Aug 10, Carter Jensen RC->KSS for Liam Hicks KSS->RC) drawn at SP139 on the EKG; other moves pinned at SP145.
  NEW: TRADE-DEADLINE BANNER pinned under the masthead with a live countdown — offers must be ACCEPTED by
  Sat Aug 22 12:00 PM (noon) CT so deals are COMPLETED & PROCESSED by ESPN's league deadline Mon Aug 24 noon.
  The banner auto-advances: countdown -> processing window (Sat noon-Mon noon) -> market closed.
  Service worker: gordo-calc-v52-2026-08-18.

GORDO NATION TRADE CALCULATOR — WEEK 18 REFRESH (2026-08-10)
  Data through Aug 9 (SP138, MP18 complete). GNDAILY 131->138 (565 shapes).
  Durability: +492 statsapi IL events (Aug 4-10) absorbed; 12 players' Hit% moved.
  Value refresh: Aug absorption 80%, F=1.361, RAW_PER_DOLLAR=466.63. Identity r=pc*pm*h: 0 violations.
  GNROS: 408 forms, 197 roles, rn 0.7255. HISTORY snapshot #11. Options: 464 players re-fed.
  Roster sync: 128 org/level, 19 injury designations, 881 season-FP updates.
  Service worker: gordo-calc-v51-2026-08-10.

GORDO NATION TRADE CALCULATOR — v50
Durability / injury system live in values · data current through August 4, 2026

WHAT CHANGED FROM v49b
  The injury system is wired into value for the first time. Three things had to be
  fixed to get there, and two of them changed numbers you have already seen.

  1. SCOPE. The durability build had been scoped to the 404 rostered players, because
     the scorer filtered `PLAYERS minus free agents`. That was never the right set.
     The score answers "how likely is this player to reach his peak again", so it
     applies to every PEAK-ANCHORED player in the universe — engine base 'vet' or
     'prod' with a peak year — which is 935, not 404. Composite-graded prospects
     (982 on 'tool') are excluded by design: durability is already inside the
     scouting grade. 'depth' (203) have no peak to return to.
     586 free agents were harvested to close the gap. 867 of the 935 now score;
     the other 68 peaked in 2026 so their window has not opened.

  2. THE 60-DAY TRANSFER BUG. statsapi writes a transfer as "transferred RHP X from
     the 15-day injured list to the 60-day injured list". Both harvesters matched the
     FIRST "N-day injured list" in that sentence, so they stored the list the player
     came FROM. 553 of 554 transfers were mis-parsed, the escalation to 60-day never
     fired, and 676 spells across 386 players scored .02 instead of .05 — the bug
     systematically under-weighted the most severe injuries, which are exactly the
     ones the score exists to catch. It was present in the v49b spine too.
     Fixing it moved stint-length agreement with ESPN from 73.8% to 94.2% on the
     four snapshots and from 59.0% to 95.6% on a fresh live capture.

  3. DAY-TO-DAY DOES NOT TOUCH VALUE. The DTD layer is seed-only and materially
     incomplete — statsapi carries no DTD at all, and the news API retains roughly
     three months per active player. Folding it in would penalise whoever happened to
     land in the seed rather than whoever is actually fragile. It is still computed
     and reported, as `dtd_score_diagnostic_only`, for the forward-accrual work.

HOW IT ENTERS VALUE
  Hit%  =  healthy base  −  applied(durability)  −  elite-velo TJ  +  ir
  RA    =  pure ceiling × pace multiplier × Hit%

  applied() is a SOFT KNEE, not a cap:
      pen(d) = d                                            for d ≤ 0.15
      pen(d) = 0.15 + 0.07 × (1 − exp(−(d−0.15)/0.07))      above it
  Identity below 0.15 (the 90th percentile of the 867 scored), then asymptotic toward
  0.22, which it never reaches — the largest applied penalty is 0.217, on a raw
  score of 0.38.

  The ceiling was FITTED, not chosen. Repeated 5-fold cross-validation against
  observed peak-return (current pace ÷ peak value, controlling for age and
  years-since-peak) over a grid of flat caps and soft knees put the optimum at a
  soft knee of 0.21 in both the healthy (n=424) and full (n=539) post-peak samples.
  0.22 is that optimum on the grid the league reasons in.

  Two things fell out of the same fit:
  · A ceiling IS justified. Linear-with-no-ceiling loses to every saturating shape
    (CV RMSE 0.41880 vs 0.41787), so the relationship between IL history and failure
    to return to peak genuinely flattens out.
  · A flat cap is not. All 83 players above 0.15 would collapse onto a single penalty
    value; the knee gives 18 distinct ones, so a 0.38 still outranks a 0.16.
  Resolution is weak: ceilings from 0.19 to 0.31 sit within 0.1% of the best CV
  error. Read 0.22 as the centre of a range, not a precise value.

  The applied score REPLACES the hand-applied "post-peak IL" haircut that 143 players
  carried. That number was an age heuristic — 114 of 119 penalised players were
  vet-base, median age 33 — while the score measures the actual IL history; the
  un-penalised group medianed age 28 and included 108 players with real IL history
  and no haircut at all. Keeping both would have priced the same risk twice.

  Two things were deliberately NOT folded in, because they price different mechanisms:
  `ir` (the current IL designation — "hurt right now") and the elite-velo TJ −0.05
  ("TJ risk profile"). Both keep their own rows in the inspector.

  One player, Keaton Winn, still carries a hand haircut: he peaked in 2026 so his
  window has not opened and the score cannot speak to him yet.

EFFECT ON VALUES
  626 of 867 scored players repriced — 582 down, 44 up, net −25,681 RA (−$52).
  Largest markdowns are free-agent arms that had never carried any injury penalty:
  Luis Severino −$0.50, Shane Bieber −$0.48, Cristian Javier −$0.46, Spencer Strider
  −$0.44, Zach Eflin −$0.43, Brandon Woodruff −$0.42.
  Largest markups are players the hand haircut had over-penalised relative to their
  measured history: Chris Sale +$0.17, Byron Buxton +$0.14, Drew Rasmussen +$0.13,
  Kevin Gausman +$0.13.
  Mike Trout: raw 0.27 (9 stints, 3 of them 60-day, over a 9.6-year window),
  compressed to −0.207, Hit% 0.80 → 0.69, 892 → 772 RA ($1.79 → $1.55).

AUDIT
  2,348 assertions replayed against ESPN, none of it merged into the spine.
    four snapshots, rostered players     1,389 comparable   98.7% correct
    fresh live capture, whole universe     912 comparable   98.4% correct
    of which newly harvested this pass     569 comparable   97.9% correct
  Zero name-bridge failures in either source — nothing observed on the IL with no
  statsapi history. 583 of 586 new targets bridged automatically; Logan Allen and
  Jose Fermin resolved on exact age, and Luis Ortiz is a flagged manual resolution
  (both candidates list as "P" and neither birth date matches v49b's age, so he was
  settled on role and peak season instead).
  The snapshots' free-agent block carries no status column, so the four historical
  dates can say nothing about the 586 — that is why a fresh capture was taken.

CALIBRATION — MEASURED, DELIBERATELY NOT APPLIED
  The same fit that set the ceiling says the whole curve wants a scale factor of
  about 1.4× on top (95% CI [0.55, 2.28]). At 1.4×, a durability of 0.10 would cost
  0.141 of Hit% rather than 0.100 — a change touching hundreds of players, not just
  the 83 in the tail. 1.0 sits well inside that interval, and one partial season of
  pace ÷ peak is not enough to justify repricing everyone by 40%. Left at 1.0.

  Position-specific curves were tested and not applied. F(3,414) = 0.47, p = 0.70.
  But that test is underpowered — a group's slope would have to differ from the pool
  by more than the pooled slope itself to clear p<.05 — so this is "not yet
  answerable" rather than "no difference". Point estimates, for the record:
  SP −0.66, RP −1.66, C −1.95, hitters −1.49. Starting pitchers showing the WEAKEST
  relationship is the opposite of intuition and worth a second look with more data.

WHAT'S IN THIS BUILD
  index.html          desktop calculator + all page tools
  mobile.html         mobile layout, same data (payload verified byte-identical)
  service-worker.js   offline cache, version gordo-calc-v50-2026-08-04
  manifest.json       PWA manifest
  icon-*.png          app icons

DATA STATE
  PLAYERS     2,122 valuations; 867 carry a durability score
  new fields  dur (raw score), durp (applied penalty), durn / dur60 (stint counts),
              durw (post-peak window length in seasons)
  GNDAILY / GNROS / HISTORY / OPTIONS unchanged from v49b

THE INSPECTOR
  The player inspector now shows a Durability row with the stint counts, the window
  length, and the raw score where the knee compressed it. A scored player with no
  post-peak IL history reads "no post-peak IL history (clean over Ny)" rather than
  showing nothing, so a clean record is distinguishable from an unmeasured one. Read
  the window length before trusting a clean reading — a player who peaked in 2025 has
  a 0.6-season window, which is not yet evidence of anything.

INSTALLING
  Replace the contents of your calculator folder with these files. The service-worker
  version changed, so the browser fetches the new build on next load; Cmd-Shift-R
  forces it.

STILL OPEN
  · The window opens the season AFTER the peak, so a player who broke down badly and
    then posted one peak season resets to clean. Drew Rasmussen scores 0.00 because
    his elbow history predates his 2025 peak. Worth deciding whether that is right.
  · Durability is a COUNT over a window that runs from 0.6 to 12.6 seasons, so it
    correlates +0.60 with years-since-peak — partly measuring "how long ago you
    peaked", which the engine already prices through peak regression. A rate version
    (burden per window-season) correlates just −0.10 with window length and predicts
    equally well (partial r −0.143 vs −0.147). Same signal, artefact removed. This is
    the highest-value change left.
  · Log peak-return weekly from the HISTORY snapshots. The whole calibration section
    above rests on a single cross-section of one partial season; a few seasons of
    observations per player would settle both the scale factor and the position
    question properly.
  · DTD forward accrual from the news API — now unblocked, and it accrues weekly
    rather than backfilling history.
  · Wire the harvest into the weekly runbook. The bridge is built; saving the packed
    spine straight into the league folder from the browser is the channel that works.
  · Feed MiLB_Log into the next scouting regrade rather than the durability score.

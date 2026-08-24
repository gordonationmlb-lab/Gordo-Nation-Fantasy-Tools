GORDO NATION TRADE CALCULATOR — WEEK 20 REFRESH (2026-08-24)
  Data through Aug 23 (SP152, MP20 complete). DEADLINE DEALS PROCESSED.
  Roster sync: 49 org/level changes, 4 drops to FA, 2 players bridged (Justin Martinez linked;
    Seth Halvorsen re-pointed from a stale duplicate ESPN id). 0 unbridged.
  THE DEADLINE: 4 deals / 13 players, accepted before Sat noon and processed Mon morning —
    RC<->CT (Langford + J. Holliday for Jhoan Duran + R. Anthony), RC<->KSS (Kirby + Webb for
    G. Williams), RC<->KCG (Bichette for Jarren Duran), HC<->BD (Chapman + Sheehan for Booser +
    Weathers). Season total 11 manager-to-manager trades. Banner auto-flipped to MARKET CLOSED.
  Injury sync: 39 designation changes; 79 rostered players carrying a designation.
  Value refresh: F=1.235 (~131.2 team games), Aug absorption 0.80. 708 pace updates, 507 pace-mult
    updates (Honeymoon/Book gate honoured), 521 repriced. Identity r=pc*pm*h at 0 violations.
  ANCHOR RE-FLOATED: RAW_PER_DOLLAR 474.73 -> 475.02, holding the average fantasy-point-scoring
    player at exactly $1.00 per the commissioner's standing ruling.
  GNDAILY 145 -> 152 (574 shapes; 5 new, 1 padded). Membership + 7 txn nodes for the week's
    4 adds / 4 drops / 31 intra-org moves / 14 cross-org legs.
  GNROS: 372 forms refreshed, 3 new; 113 roles re-fed (23/30 carryover + the exact Aug 17-23
    [SV,HD,BS] delta); rn 0.7340 -> 0.7473 over 101 rostered RPs.
  HISTORY snapshot #13 (2026-08-24) for the manager-comparison EKG.
  OPTIONS TRACKER rebuilt from the processed log: 495 players, burns 0:281 / 1:180 / 2:34,
    ZERO over the two-option limit.
  *** PALENCIA — RULE 5 RECAPTURE, NO OPTION CHARGED ***
    Daniel Palencia was drafted from C-Town by River Cats (Jul 14), released to waivers by River
    Cats on Aug 22, and reacquired by C-Town onto Clam Shack. Article V(b)(4)(C)(ii) expressly
    permits the AAA placement, and V(b)(4)(C)(i) excuses the option — per Article VI(d) the ONLY
    exception to VI(b). COMMISSIONER'S RULING Aug 24, 2026: exemption GRANTED. The election was
    announced in the league Discord at 9:00 AM CT on Aug 22, four minutes after the 8:56 AM release
    and well inside the two-day window; ESPN's waiver mechanics completed the transfer at 12:05 PM
    CT on Aug 24, three hours past the two-day mark. The right was exercised in time — only the
    platform's processing ran long, the same distinction the league already applies to the trade
    deadline. Subject to appeal. Palencia stands at 2 burns / 0 remaining and is COMPLIANT.
    Feed note: ESPN's raw feed stamped the Aug 22 release as coming from Flying Squirrels (AAA);
    the ESPN transaction view shows River Cats (MLB), which the commissioner confirmed. The ledger
    follows the transaction view — otherwise the burn never triggers and the exemption would appear
    unused rather than exercised.
  Rule 5 selector: Palencia now carries a recaptured flag so the tracker reads a legal terminal
    state instead of flagging him as missing from the drafting club.
  Service worker: gordo-calc-v56-2026-08-24.

TARGETED CLASSIFICATION PASS — PHASE / PACE-GATE / MATURATION (2026-08-24)
  Commissioner-authorised targeted pass; the full FV/tool-grade re-sweep is deferred to the offseason.
  Last prior classification work was Jun 11-24 (ENGINE/MATRIX/RAMP/SCARCITY/REPHASE) — 9-10 weeks stale.
  FIX A - PACE-MULTIPLIER GATE RESTORED (91 players). Methodology 13/20.10 holds Honeymoon- and
    Book-phase T3 at pace-mult 1.00. The gate was applied Jun 15 ("PACE GATE v14") and REGRESSED in a
    later refresh — players carried a June note saying the gate set them to 1.00 while the live board
    showed 1.5 or 0.5. Restored, together with the hard short-circuits (on-IL, Pure<300, pace<=50).
    NOTE: "on the IL" is the four DL designations only — DTD and OUT keep their pace multiplier.
  FIX B - PHASE CATCH-UP (68 promotions). Phase re-tested against cumulative FP (2025 + 2026-to-date)
    on the 19.4 boundaries (hitters 150/500, pitchers 250/750). Where the Jun-11 pass recorded a true
    cumulative it is carried forward plus 2026 growth; otherwise 2026-to-date alone is used, a safe
    lower bound. The test can only PROMOTE, never demote. Tool-basis phase multiplies the bust
    (x0.80/x1.15/x1.00 per 20.7); production-basis multiplies Hit% (x1.20/x0.85/x1.00 per 19.4).
    Additive Hit% modifiers (durability, outlier, IL-stack) measured off each live record and preserved.
  FIX C - MATURATION EXPIRY (25 released, 3 deferred). Methodology 9: the stage discount expires at
    Established. Released ONLY where the arithmetic proves the discount is inside Pure; Chandler,
    Sasaki and Grissom carry other ceiling factors (SP/RP blend, post-hoc re-anchor) so their release
    is deferred to the offseason sweep rather than guessed.
  RESULT: 134 players repriced (95 up, 39 down), identity r = pc*pm*h at 0 violations across all 2,123.
  DOLLAR ANCHOR RE-FLOATED, RAW_PER_DOLLAR 467.65 -> 474.73 (+1.51%), per commissioner's ruling:
  the average fantasy-point-scoring player must ALWAYS equal $1.00. Holding the old anchor after the
  reclass left the average player priced at $1.015 — the invariant that defines the scale was broken.
  A dollar figure is a RELATIVE measure (a player against the field), so a stale anchor is not a
  harmless scale offset; it misstates every player. 1,361 dollar values restated; relative ordering
  is unchanged (rescaling is monotone). Note the 20.20 "anchor held" precedent does NOT apply here:
  that case was a POOL change (adding 720 minor leaguers would have moved the mean by composition
  alone). This was a VALUE change inside a fixed pool, where the mean moved because real values moved
  — the two cases resolve opposite ways. Issue 19's printed dollars sit on the old anchor and are
  ~1.5% high against this board; disclose in the Issue 20 correction log.
  Service worker: gordo-calc-v55-2026-08-24.

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

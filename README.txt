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

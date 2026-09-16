GORDO NATION TRADE CALCULATOR — v51.4  THE OPTIONS LEDGER, REBUILT (2026-09-16)
  Same pull and data window as v51.0-v51.3: scoringPeriod 173, matchup period 22 — the
  championship round — one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data.
  F = 162/149 = 1.0872; September absorption 0.90. No weekly refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v79-2026-09-13-v51.4.  GN_BUILD v51.4, GN_DATA_THROUGH 2026-09-13.

  v51.4 touches NO valuation input. Dynasty values, ceilings, org ranks, the injury module and
  every constant in it are byte-identical to v51.3. What changes is the OPTIONS TRACKER: three
  parse defects are fixed, the ledger is rebuilt from the full season, and the Rule 5 note in the
  record card is repaired. 14 players' burn counts move; all 14 move UP; 10 of them are now out
  of options. Nobody is over the limit.

  Run with bump_build_v51_1.py v51.4, patch_ui_v51_4.py --apply, patch_options_parse_v51_4.py
  --apply and rebuild_options_v51.4.py --apply.
  Acceptance: the roster-reconstruction gate in rebuild_options_v51.4.py, then update_options.py
  reproducing 1,151 of 1,151 stored events with zero divergence and zero new burns.

================================================================================
WHAT CHANGED IN v51.4 — three parse defects, a full-season rebuild, one CSS collapse

  HOW THIS STARTED. The commissioner read Dillon Dingler's card. High Cheddar released him
  Sep 7; hicheddar AAA — the same organisation's AAA club — took him back Sep 10. That is an MLB
  release followed by a AAA acquisition in the same season, which is an option under Article
  VI(b)(3), and the card charged nothing. Time in the free-agent pool is irrelevant to VI(b)(3);
  the only question the rule asks is what the most-immediate prior roster status was.

  DEFECT 1 — mt 180 and mt 181 are INVERTED. They are the two halves of a waiver claim: 180 is
  the player CLAIMED, 181 the player dropped to make room. The classifier had 181 adding and 180
  dropping. 13 adds were filed as drops, 12 drops as adds. Three independent proofs: replaying
  the feed onto the live rosters, the swap fixes six players the old reading strands in free
  agency who are in fact rostered (Dingler on hicheddar AAA, Salvador Perez, Emerson Hancock,
  Carson Benge, Jacob Latz, Ian Seymour); the stored ledger held impossible sequences under the
  old reading (AJ Blubaugh "dropped by hicheddar AAA" Mar 27, then TRADED FROM hicheddar AAA
  Apr 4; Matt Svanson added twice with no drop between); and every 180 is paired same-day,
  same-club with a 181, which is what a claim plus its corresponding drop looks like.

  DEFECT 2 — mt 239's `from` is a LINEUP SLOT, not a club. The dropping club is in `for`. Slot
  ids and team ids share the range 0..17, so is_team() said yes to a slot and the drop was filed
  against whatever club carried that number: 36 of 52 drops to the wrong club, 16 to "FA/Waivers
  (None)". Dingler's Sep 7 release reads from=0 — slot 0 is CATCHER, which is what he is. Brad
  Lord's Jun 16 release by TheMidwestBears (MLB) reads from=15, slot 15 is RP, and it was filed
  as "Dropped by Flying Squirrels (AAA)". This is not a misprinted name. A drop sets the player's
  level, and level is the entire input to VI(b)(3): an MLB release filed as a AAA release makes
  the next AAA add read AAA->AAA and charge nothing.

  DEFECT 3 — a pending trade could never be upgraded to a processed one. The weekly extension
  keeps, per player, only events strictly NEWER than that player's newest stored event. A trade
  accepted and processed on the same day writes the 224 first; the 244 that follows lands ON the
  watermark and is suppressed for good. Five of Mike F's Sep 7 demotions were still sitting in
  the ledger as "Trade pending" — all five processed (DeLauter, Leahy, Murakami and Neto are on
  PCA and Jarren Duran Fan Fest right now; Pfaadt was demoted and then dropped Sep 9), and all
  five are MLB->AAA. Related: mt 241 is the veto, and the parser did not read it, so a vetoed
  acceptance sat in the ledger as a pending burn that could never land and someone annotated it
  by hand every week (Ian Seymour, Aug 22). It is derived now.

  WHY A REBUILD AND NOT AN EXTENSION. update_options.py extends because ESPN's activity feed
  "only returns a trailing window" — true of the 500-record pull it was written against, not of
  this one: the v51.0 pull carries 792 records / 2,131 messages spanning 2026-02-19 to
  2026-09-12, the whole season. The defects above are historical — baked into events already
  stored — and an extension by construction never revisits those.

  THE RULE SET IS UNCHANGED. Article VI(b) as the Week 20 build states it: (b)(1) own MLB -> own
  AAA, (b)(2) own MLB -> another manager's AAA, both as a processed trade; (b)(3) an add to a AAA
  club when the most-immediate prior roster status was MLB. Preseason rows set level and never
  burn. Art. V(b)(4)(C)(i) Rule 5 recapture remains the only exemption (Art. VI(d)) and is still
  granted to Palencia alone, on the commissioner's Aug 24 ruling.

  THE GATE. Nothing was written until the corrected parse reconstructed the live rosters at least
  as well as the parse it replaces (2 players on the wrong club against 8; 21 phantom-rostered
  against 28) and until every player already on file was reproduced. Stored 508 players / 1,158
  events; rebuilt 508 players / 1,158 events — the same universe, reclassified. Burns 259 -> 273.
  Histogram {0:289, 1:179, 2:40} -> {0:285, 1:173, 2:50}. Over the limit: none.

  THE 14 CORRECTIONS, none downward:
    Adrian Morejon      1 -> 2  OUT   Jul 16 added by DirtySpikes AAA off an MLB roster
    Brad Lord           0 -> 1        Jun 18 added by KC Royales off an MLB roster
    Brandon Pfaadt      0 -> 1        Sep 7  KC Gray -> KC Royales, processed, not pending
    Carson Benge        1 -> 2  OUT   Jul 16 added by Minion AAA off an MLB roster
    Chase DeLauter      1 -> 2  OUT   Sep 7  KC Gray -> KC Royales, processed, not pending
    Dillon Dingler      1 -> 2  OUT   Sep 10 added by hicheddar AAA off an MLB roster
    Fernando Cruz       0 -> 1        Jul 29 added by hicheddar AAA off an MLB roster
    Ian Seymour         0 -> 1        Jun 27 added by Flying Squirrels off an MLB roster
    Kyle Leahy          1 -> 2  OUT   Sep 7  KC Gray -> KC Royales, processed, not pending
    Munetaka Murakami   1 -> 2  OUT   Sep 7  KC Gray -> KC Royales, processed, not pending
    Payton Tolle        1 -> 2  OUT   Jun 28 River Cats -> Flying Squirrels
    Pete Fairbanks      1 -> 2  OUT   Aug 26 added by hicheddar AAA off an MLB roster
    Will Warren         1 -> 2  OUT   Jul 13 Dirty Spikes -> DirtySpikes AAA
    Zach Neto           1 -> 2  OUT   Sep 7  KC Gray -> KC Royales, processed, not pending

  RULE 5 — DINGLER REVERTED, AND THE CARD SAYS SO WITHOUT RULING. Art. V(b)(4)(C)(i) shelters a
  released draftee reacquired BY THE CLUB HE WAS DRAFTED FROM, WITHIN TWO DAYS. Dingler fails
  both: three days, and hicheddar AAA is the drafting organisation's own club, not Midwest Bears.
  Art. V(b)(4)(C)(iii) governs instead — he reverted to ordinary property on clearance, and that
  clause is explicit that no exception to VI(b)(3) is granted, so the option is charged. On the
  keeper tag, Advisory Opinion 2026-R5-02 (Jul 8) is directly on point: Holding 5 leaves a
  reacquired draftee in the drafting organisation's hands as ordinary property under the rules as
  written, and §IV names this exact sequence, declines to bar it by opinion, and refers an
  anti-circumvention amendment to the membership for the next-season vote. The record card states
  that and marks the commissioner's determination as pending. RULE5 entries may now carry
  `reverted`, `reverted_on` and `reverted_note`; the blue note branches on it rather than
  claiming a reverted player "may NOT be demoted", which is false once he has reverted.

  CSS — THE RULE 5 NOTE RENDERED VERTICALLY. The Options record sits in a .dual-grid half (575px
  of content at a 1280px viewport) and .player-card split that in two again, so each .formula-row
  had 254px. The only rule that unstacks .player-card is @media (max-width:700px), which keys off
  the VIEWPORT — it can never fire for a card that is narrow because of its CONTAINER. Inside
  254px the note's inline `grid-template-columns:auto 1fr` gave the label its max-content 243.5px
  and the text 0px; v50.22's min-width:0 on .formula-row>* let the track shrink past min-content
  instead of holding there, and overflow-wrap:break-word then set 400 characters one per line —
  measured at 0px wide and 3,752px tall. Fixed twice over: the card now sizes off ITSELF
  (auto-fit, minmax(min(320px,100%),1fr) — the min() is load-bearing, a bare 320px floor is a
  HARD minimum and overflowed a 390px phone by 18px), and the note stacks label over text so no
  track width can collapse it again. Verified headless at 360 / 390 / 768 / 1024 / 1280 / 1600:
  zero overflow at every width, note 246-549px wide and 204-464px tall, background #edf1f7.
  The same squeeze was quietly cramping the transaction rows, whose "- 1 option" chips were
  rendering into a 0px track; they read normally now.

================================================================================
GORDO NATION TRADE CALCULATOR — v51.3  THE EXIT CLASS CONSTANTS (2026-09-14)
  Same pull and data window as v51.0, v51.1 and v51.2: scoringPeriod 173, matchup period 22 — the
  championship round, SP167-180 — one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data.
  F = 162/149 = 1.0872; September absorption 0.90. No weekly refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v78-2026-09-13-v51.3.  GN_BUILD v51.3, GN_DATA_THROUGH 2026-09-13.

  v51.3 changes SIX CONSTANTS and re-floats a seventh. The injury module's structure is again
  untouched — same four terms, same assembly, still Durability v2.2. What moves is the CLASS
  MULTIPLIER under the exit hazard, and the calibration scalar that has to be re-fitted with it.

  Run with bump_build_v51_1.py v51.3, then patch_injury_v51_3.py, apply_injury_v2.py --apply,
  patch_ui_v51_3.py --apply, stamp.py --apply and resync_ceiling_workbook_v51.3.py --apply.
  Acceptance: verify_calc.py, FAIL 0.

================================================================================
WHAT CHANGED IN v51.3 — six exit class constants, re-fitted instead of assumed
  WHERE THIS CAME FROM. v51.2's gate left an aggregate model that was calibrated in the mean. The
  follow-up work asked whether the exit hazard could be split finer — by injury class and by age.
  A full class x age grid was built and tested out-of-fold and it LOST: MAE 239.5 against the
  shipped 237.9, every confidence interval straddling zero. The grid was declined. See
  claude/exit-grid-proposal-tested-and-declined.md.

  What the grid did do is expose constants in the SHIPPED table that were wrong by more than a
  factor of two on their own samples. An aggregate MAE over 303 players cannot see a constant that
  is backwards on a class holding twenty men; that is an argument for fixing the constant on its
  own evidence, not for adding machinery. Six were fixed. Two more were proposed and are NOT in
  this build (see HELD BACK, below).

  THE EVIDENCE BASE is the same one the shipped EXIT table was built on: 2021-2024 IL episodes with
  at least two full seasons of follow-up, "never returned" measured to 2026-09-13. Each class is
  estimated as a ratio to its role x list pool and shrunk toward that pool at K = 12, the constant
  the held-out sweep in backtest/micro_channels.py chose. No age term and no interaction — those
  are what lost.

  THE SIX CONSTANTS (60-day list only; the short list is untouched in this build):

      class                              n   realized   pool    was      now
      P  UCL / Tommy John              164      12.2%  21.8%   x1.00    x0.58
      P  elbow, not a reconstruction    62      37.1%  21.8%   x1.00    x1.56
      P  forearm / flexor, not a TJ     39      33.3%  21.8%   x1.00    x1.38
      P  shoulder, soft tissue         138      32.6%  21.8%   x1.50    x1.45
      P  shoulder, structural           18      33.3%  21.8%   x1.80    x1.45
      H  named surgery                  31      22.6%  10.8%   x0.75*   x1.70
                                                (* x1.40 where the category was lower-body)

  THE HEADLINE. The module had the two elbow classes EXACTLY INVERTED. A pitcher who has had a
  reconstruction comes back: 12.2% never played in the majors again, against a 21.8% pool. A 60-day
  elbow that is NOT a reconstruction is the dangerous one: 37.1%. Both were priced at the pool.
  Forearm/flexor behaves like the dangerous end too. Tommy John is now the SAFE elbow injury in
  this calculator, because that is what the record says.

  THE SHOULDER SUBTYPE, which Dustin's capsule objection produced in v2.1, does not survive on the
  exit term: structural 33.3% (n=18) and soft tissue 32.6% (n=138) are the same number. Both are
  well above the pool; neither is distinguishable from the other. x1.80 / x1.50 is finer than the
  data supports, so both go to x1.45. The subtype KEEPS its rate term (-20% against +2.6%) and its
  return-time curve (surgical, 53% back by day 416 against 89%), where it was actually measured.

  CLASS RESOLUTION, and it is the part that is not a one-line edit. cat_mult() keyed on the
  category string, and the transaction feed almost never writes "UCL": 60 of 971 pitcher 60-day
  episodes carry cat 'ucl' while 203 carry the TJ flag. Editing CATMULT['P']['ucl'] would have
  reached under a third of actual reconstructions and left the rest mis-priced. So exit_class()
  resolves the class first, in the order the constants were fitted in:

      pitchers : TJ flag OR category 'ucl' > structural shoulder > named surgery > module category
      hitters  : named surgery > module category

  The 'ucl' category counts as a reconstruction even without the flag. In the feed the two are the
  same set (68 of 68 'ucl' episodes carry the flag), which is why the fitted cell is unaffected —
  but the NEWS-FACTS layer writes cat='ucl' from a surgery report without always setting tj, and 14
  overrides do exactly that. Keying on the flag alone dropped Justin Steele and Robert Stephenson
  into `surgery_other` and they never saw the correction. Caught by reading the board.

  THE ORDER IS LOAD-BEARING. An elbow with a named surgery but no TJ flag is `surgery_other`, NOT
  `elb` — the 37.1% was measured on non-surgical elbows and must not be charged to surgical ones.
  `surgery_other` has no constant of its own and falls through to CATMULT exactly as before. This
  was caught in review: a first pass applied x1.56 to every non-TJ elbow and moved Spencer
  Schwellenbach 111 RA on a population his cell was never fitted on.

  EXIT_CALIB 1.50 -> 1.58, RE-FITTED. The v51.2 scalar was fitted against the OLD class multipliers,
  so changing them shifts the level and the scalar cannot be left alone. Re-fitted by the same
  procedure on the same 2024 cohort: predicted 13.9% against a realized 13.9%, ratio 1.00.

  WHAT THE BACK-TEST SAYS. The gate was re-run with the new constants in place:
      MAE on the injured cohort   238.2 against 237.9 shipped   (95% CI -0.7 to +1.3)
      bias                        +7.2 against +9.2 shipped     (better)
      2024 calibration ratio      1.00 against 1.01 shipped
      healthy cohort              provably unchanged, to 0.00e+00 — a player who is not on an
                                  injured list has no exit term, so none of this can reach him
  No significant improvement, and none was expected: the aggregate test is underpowered to see a
  correction that touches twenty records out of 303, which is exactly why these are argued on their
  own samples. What the gate is for here is ABSENCE OF HARM, and it shows absence of harm.

  BOARD EFFECT. RAW 526.16 -> 525.39; board RA 806,706 -> 805,599 (-0.14%). Thirty-three rostered
  records move, but only thirteen by more than four points — the rest is the calibration step
  touching short-list players by a point or two. The ones that matter:

      down   Spencer Strider       Dirty Spikes      elbow, no reconstruction   1060 ->  818  -242
             Colt Emerson          River Cats        season-ending wrist surgery 760 ->  626  -134
             Ryan Helsley          Balking Dead      elbow, no reconstruction    566 ->  475   -91
             Robert Suarez         River Cats        elbow, no reconstruction    455 ->  376   -79
             Connelly Early        River Cats        elbow, no reconstruction    611 ->  539   -72
      up     Justin Steele         Balking Dead      UCL revision                527 ->  622   +95
             Hunter Greene         River Cats        second Tommy John           709 ->  760   +51
             Felix Bautista        Dirty Spikes      structural shoulder         441 ->  478   +37
             Carlos Estevez        Balking Dead      structural shoulder         319 ->  349   +30
             Robert Stephenson     MidwestBears      ligament + flexor repair    244 ->  274   +30
             Keegan Akin           Balking Dead      Tommy John                  236 ->  259   +23

  Colt Emerson is the hitter-surgery constant doing what it was fitted to do: a season-ending wrist
  operation was priced at x0.75, BELOW average risk, because it fell in the `other` bucket. It is
  now x1.70. Among free agents the biggest moves are Giolito (long-absence elbow, down) and Eflin
  and Severino (reconstruction and structural shoulder, up).

  ORG RA: River Cats 53,773 -> 53,522 (-0.5%), Dirty Spikes 45,689 -> 45,466 (-0.5%), Balking Dead
  41,532 -> 41,588 (+0.1%), MidwestBears 42,479 -> 42,499, KC Gray 52,835 -> 52,833, Kansas
  Sunflower Seeds 47,702 -> 47,701, High Cheddar 44,957 -> 44,951, C-Town 43,051 -> 43,045. The two
  clubs holding 60-day elbows pay for it; nobody else moves materially.

  VERIFICATION. The study rule and the shipped code are two independent implementations of the same
  resolution, so they were compared on EVERY episode in the feed rather than on a sample: 4,892 of
  4,892 agree (backtest/verify_v513_impl.py). 659 episodes get a different multiplier than under
  v51.2, all of them on the 60-day list, as intended.

  HELD BACK — two corrections that did NOT clear the gate and are not in this build:
    * Hitter foot/ankle x1.40 -> x0.29. n=15 with ZERO realized events; the value is entirely the
      shrinkage prior, and the gate drifts the wrong way (+0.4 MAE). It needs a floor and more data.
    * Giving the short list a class multiplier at all. cat_mult() returns 1.0 whenever il60 is
      false, and the spread there is real (hitter knee 5.3% on n=76 against hand 1.2% on n=167,
      pool 2.0%). But it moves 18 records for a net +45 RA, and stacking it with the foot
      correction pushed the MAE confidence interval to (+0.0 to +3.2) — significant harm, in the
      wrong direction. Broadest change, smallest stakes, weakest evidence: it waits.
  Both are written up in claude/v51.3-proposal-four-exit-constants.md.

================================================================================
WHAT CHANGED IN v51.2 — the exit prior, calibrated against what actually happened
  THE GATE. The spec had carried an open item since v51.0: "2024->2025 and 2025->2026 back-tests
  with v2 in place of the v50 haircut ... lower MAE on the injured cohort, calibrated exit
  probabilities, no loss on the healthy cohort." It was run on 15 Sep 2026. Artifacts:
  backtest/ in this folder; write-up: claude/durability-v2.2-backtest-gate-results.md.

  WHAT IT FOUND. The module beats the retired v50 haircut on the injured cohort by 30.9 points of
  MAE (95% CI +16.4 to +45.5) and costs 0.18 points of 248 on healthy players — the framework
  change is vindicated. But the exit probabilities are not calibrated. Over the 2024 cohort, the
  only one with two full seasons of follow-up, the module said 9.3% of the players it had on an
  injured list would never play in the majors again. 13.9% did not. The buckets are monotone, so S
  RANKS correctly; only the level is wrong, by about half again.

  THE CHANGE. EXIT_CALIB = 1.50, carried in build.json as exit_calibration, applied to p0 inside
  exit_p0() — the PRIOR, not the posterior. The time update

      p_exit(t) = p0 / (p0 + (1 - p0)(1 - F(t)))

  is a correct Bayesian statement given a correct prior; scaling its OUTPUT would leave the wrong
  prior in place and break the identity. 1.50 is fitted rather than chosen: it is the scalar whose
  output is calibrated (ratio 1.01) after the update runs. Every record the module touches states
  it — "exit 36% base (back-tested x1.50) -> 39% at day 165".

  WHAT IT DID NOT CHANGE. Nothing else from the gate has been acted on. Two findings are recorded
  and deliberately not built: only one of six rate classes (surgery, realized -18% against the
  shipped -15%) verifies against a clean pre-injury base, and the module is well calibrated for
  pitchers (+4 points of bias) while over-valuing hitters coming off an injured list by 56. The
  structural-shoulder -15/-25 question the gate was supposed to settle cannot be settled from two
  seasons — five cases, two usable, both the same pitcher — and stays a judgment call.

  WHAT IT DID TO THE BOARD. RAW 530.98 -> 526.16 (-0.9%); board RA 813,667 -> 806,706 (-0.9%).
  259 records carry the calibrated base. Nobody the module leaves alone moved at all.
  ORG RA: River Cats 54,181 -> 53,773 (-0.8%), Dirty Spikes 46,025 -> 45,689 (-0.7%), Balking
     Dead 41,764 -> 41,532 (-0.6%), MidwestBears 42,575 -> 42,479 (-0.2%), C-Town 43,096 ->
     43,051 (-0.1%), High Cheddar 44,997 -> 44,957 (-0.1%), KC Gray 52,844 -> 52,835 and Kansas
     Sunflower Seeds 47,711 -> 47,702 (both -0.0%); FA pool 440,474 -> 434,688 (-1.3%).
     The clubs holding hurt players pay for it, which is the point.

================================================================================
WHAT v51.1 CHANGED — two rules, both stated on every record they touch (carried forward)

  1. RETURN-SEASON RUST. In v51.0 the rate term R (the per-inning penalty after a return: surgery
     -15%, structural shoulder -20%, repeat elbow -14%, ...) was anchored to the calendar: full in
     2027, half in 2028, gone after — whatever season the player actually came back in. For a
     pitcher who misses all of 2027 that put the full rust on a season he does not pitch (where
     the zero availability made it moot) and only the half-strength term on his real first season
     back. Greene read 2027 0 / 2028 1,104 / 2029 1,134: the least rust in the year he will carry
     the most. v2.2 anchors it to the RETURN SEASON — the season that contains the expected return
     date (k_ret: 0 = 2027, 1 = 2028, ...): full R there on the share of that season he is back
     for, R/2 the season after, survival S alone beyond, and every season before the return is a
     zero line. Closed episodes keep the spec's decay by months from the return to opening day
     (full <= 8, half 8-20, none beyond).
     UCL WORKLOAD FACTOR V = 0.85. The all-player study's 82 paired UCL returners lost 12% per
     inning in the first window back (that is the R term) AND threw fewer of them: innings per 30
     days 20.7 -> 17.4, starts share 0.65 -> 0.54, because clubs cap the workload. In this scoring
     fewer innings is fewer points, so the return season of a UCL-class pitcher return
     (reconstruction-length: surgery named, or 300+ days out — not a sprain rested for a month;
     pitchers only, the finding is innings) carries x0.85 on top of R. It rides with a full-weight
     UCL term: the return season for a player still out, 2027 for a return inside the last 8
     months before opening day (Steele, Houck, Lopez, Montgomery, J. Martinez).
  2. ASSET-VALUE HEADLINE. r has never been a coming-season forecast: it is the ceiling-blended
     asset value for everyone, and a prospect who will spend all of 2027 in the minors keeps his
     full r. The v2.1 module was the only thing that turned r into "what he produces in 2027",
     and only for hurt players — so Greene read 0 on the Trade Desk's default 1-year window. Now
        r = round( Pure x Pace x Hit% x ia ),   ia = (1 + R) x V x S x (1 - A_rec) x 0.90^deferral
     deferral = seasons the production is pushed back = k_ret + the share of the return season
     missed (= A_known for a 2027 return). DELTA = 0.90 per season deferred is the commissioner's
     call (the measurable part — 15% of UCL returners take longer than 591 days, i.e. past
     opening day 2028 for a 12 Aug 2026 surgery, and 8% more than two years — is 5-8% of the
     next-season line; the rest is a year of not seeing him pitch; the thin market for a 2028
     season and the AAA stash slot are left to the engine's per-window valuation, and the
     revision-TJ risk is a player-specific S question, not a time preference). The coming-season
     availability now prices only the coming season's LINE:
        f[0] = (1 + R) x V x A x S  (A = 1 - A_known - A_rec) when he is back during 2027, 0 if not;
        f[k] per the return-season schedule;   tj[k] = round(tjp[k] x Hit%(age+k) x f[k]).
     On the record: p.im = ia (the multiplier on the headline, as before), p.inj.ia, p.inj.f (ten
     year factors), p.inj.im = f[0] (the 2027 line), p.inj.im2 = f[1], k_ret, miss_ret, V, defer.
     The asset never reads below the 2027 line (0.90^x >= 1 - x on [0, 1]), asserted.

  HUNTER GREENE (River Cats, second Tommy John 12 Aug 2026, 12-18 months, return 2027-11-11):
     healthy RA 1,331 (Pure 1416 x pace 1.00 x Hit% 0.94); A_known 1.00, A_rec 0.030, R -15%
     (surgery), V 0.85, S 0.897 (10% never-return), return season 2028, deferral 1.00.
        v51.0   r 0      lines 2027 0 / 2028 1,104 / 2029 1,134 / 2030 1,043
        v51.1   r 753    lines 2027 0 / 2028   862 / 2029 1,049 / 2030 1,043
     ia = 0.85 x 0.85 x 0.897 x 0.970 x 0.90 = x0.565. His 2028 line is his first season back:
     1416 x 0.94 x (0.85 x 0.85 x 0.897); 2029 carries the half rate term; 2030 survival only.

  WHAT v51.1 DID TO THE BOARD. RAW 527.29 -> 530.98 (+0.7%); board RA 804,530 -> 813,667 (+1.1%).
  96 records moved (74 with a deferral, 34 with the workload factor, 2 by +-1 RA of rounding);
  nobody else. 762 of 2,080 priced records still carry a multiplier under 1.00 (243 of 406
  rostered); no rostered player sits under x0.50 any more (v51.0 had 8, all IL-60 pitchers).
  Every org's $ moves a little with RAW (-0.5 to -0.7 for the six that did not gain RA).

  ROSTERED MOVERS (RA v51.0 -> v51.1; im is the headline multiplier)
     Hunter Greene      River Cats     0 ->  753   x0.000 -> x0.565  return season 2028, V 0.85, deferral 1.00
     Spencer Strider    Dirty Spikes 467 -> 1191   x0.247 -> x0.630  back 2027-07-16, deferral 0.61 (repeat elbow, no V)
     Robert Suarez      River Cats   189 ->  497   x0.256 -> x0.674  back 2027-07-21, deferral 0.63
     Keegan Akin        Balking Dead  10 ->  256   x0.020 -> x0.538  TJ 15 Jul, back 2027-09-12, V 0.85, deferral 0.92
     Carlos Estevez     Balking Dead 163 ->  386   x0.226 -> x0.535  shoulder surgery, back 2027-07-12, deferral 0.59
     Rafael Devers      MidwestBears 1152 -> 1199  x0.947 -> x0.985  back 2027-04-02, deferral 0.04
     Phil Maton         MidwestBears 290 ->  305   x0.837 -> x0.880  deferral 0.05
     Justin Sterner     MidwestBears 317 ->  330   x0.703 -> x0.732  deferral 0.04
     Justin Steele      Balking Dead 716 ->  608   x0.670 -> x0.570  UCL revision, rehab 1 Sep: V 0.85 on 2027
     Justin Martinez    Dirty Spikes 634 ->  539   x0.747 -> x0.635  UCL, returned Aug 2026: V 0.85 on 2027
     Robert Stephenson  MidwestBears 317 ->  269   x0.672 -> x0.571  UCL, back 2026-12-15: V 0.85 on 2027
     (Eovaldi 870 -> 871 and B. Ashcraft 1156 -> 1155 are 4-decimal rounding of the same terms.)
  FREE-AGENT MOVERS: up — Giolito 136 -> 714, Dollander 302 -> 872, Woodruff 106 -> 566,
     M. Parker 40 -> 404, Horton 145 -> 508, Keller 0 -> 342 (return season 2028), Lauer 59 -> 380,
     Kolek 0 -> 289 (2028), Priester 242 -> 524, Sands 140 -> 416, Whisenhunt 0 -> 263 (2028);
     down (V on a 2027 return season) — P. Lopez 925 -> 786, Houck 732 -> 622, Montgomery
     635 -> 540, Montas 587 -> 499, Berrios 568 -> 483, Gonsolin 538 -> 457, Vasil 529 -> 449.
  ORG RA (v51.0 -> v51.1): River Cats 53,121 -> 54,181 (+2.0%), Dirty Spikes 45,396 -> 46,025 (+1.4%), Balking
     Dead 41,402 -> 41,764 (+0.9%), MidwestBears +0.1%, the other four unchanged; FA pool +1.6%.
     Whole-board $ (RAW moved): River Cats +1.30, Dirty Spikes +0.59, Balking Dead +0.14, Bears
     -0.51, C-Town -0.57, High Cheddar -0.59, Sunflower Seeds -0.63, KC Gray -0.70.

================================================================================
THE MODULE (apply_injury_v2.py, Durability v2.2 — report in injury_report_2026-09-13.json)
  Re-run on the v51.0 board (idempotent: the v50 terms stay retired on p.v50inj, Hit% is already
  clean, the v51.0 note stays on the record as history and a v2.2 note is written only on the 94
  records whose terms changed). New in the port: return_season(date) -> (k_ret, miss_ret);
  assemble(inj) builds f[0..9], im/im2, defer and ia from the terms and is called last, after the
  designation-only fallback and the tool-basis rule, so every path shares one assembly. The UCL
  workload flag is set in the rate loop beside the decay (pitchers, cat ucl, full weight, surgery
  or 300+ days). Tool-basis prospects: R, A_rec and V are zero (the scouting bust carries
  durability); they keep A_known, S and the deferral. build.json carries deferral_delta 0.90 and
  ucl_workload_factor 0.85; the module and the verifier read them from there.
  Return seasons on the board: 263 players out with a 2027 return, 8 with a 2028 return (Greene,
  Keller, Kolek, McDonald, Avila, Whisenhunt, Ky Bush + 1); 34 pitchers carry V; 74 records carry
  a deferral, 8 of them a full season.
  Records: 1,003 bridged, 1,077 no IL record since 2021, 12 designation-only, 8 resolved by ESPN
  activity, 10 name/age mismatches (unchanged from v51.0); review flags: Chris Martin, Brock
  Stewart (unchanged). Overrides: 128 entries, unchanged (127 auto from the news + Ragans by hand).

================================================================================
THE CALCULATOR UI (patch_ui_v51_1.py — every change is one asserted replacement in gn-app.js)
  VALUE ENGINE      gnInjFactor(p, k) reads p.inj.f[k] (falls back to im / im2 / S on a v51.0
                    record); fadeAdjustedTj and the cumulative / single-season windows follow.
                    p.im is the asset multiplier. New helpers gnInjSeasonLine(p) (the 2027 factor)
                    and gnInjReturnYear(p). Constants GN_INJURY_MODULE 'Durability v2.2',
                    GN_INJURY_DELTA 0.90, GN_UCL_WORKLOAD 0.85 (the build stamp prints the module).
  PLAYER INSPECTOR  header "Injury (asset): x0.565 (extreme)"; the injury section adds the
                    return season sentence ("Return season 2028 — the rust is anchored there ...;
                    2027 is a zero line"), the V row, the "= 2027 season line" subtotal, the
                    deferral row and "= Injury asset multiplier (1 + R) x V x S x (1 - A_rec) x
                    delta^deferral", then the factors by season; the RA section reads RA = Pure x
                    Pace x Hit% x Injury asset multiplier and prints the 2027 season line under
                    the headline with a note that the headline is what the asset is worth now and
                    the line is what he gives this season (the trajectory's Current cell); the
                    trajectory note says Current is the season line, not the headline, and names
                    the return season.
  FLOW TREE / SPINE the INJURY column adds "return season 2028 (2027 out)", "V: UCL workload",
                    "2027 season line" and "deferral 0.90^1.00" rows and ends "= INJURY (asset)";
                    step 6 of the decision spine carries the same terms.
  TRADE DESK        the injury card's text says the discount is on the asset value (the chart is
                    unchanged: healthy RA minus risk-adjusted RA per pick); the picked-row tag
                    "Inj x0.57" is the asset multiplier.
  Both pages' injury-card note rewritten for v2.2; the as-of footer says "Durability v2.2 injury
  module — return-season rust, asset-value headline" (stamp.py).
  HOTFIX, same day (patch_css_v51_1.py; service-worker cache v75 -> v76 so installed copies pick it
  up): numbers were breaking mid-token in the Inspector — Dustin: "some numbers are getting wrapped
  in the player inspector. see cole ragans. are there others?" Yes: 20 distinct rows in every section
  on both pages (Ragans' "= Pure ceiling (healthy peak = expected full-season pace)" value as
  "156 / 7", the "x Pace multiplier" label beside the evidence-rule sentence as "x / Pac / e / mu /
  ltip / lier", Griffin's proximity "-0.1 / 0", every Pure ceiling on the desktop page). The cause
  predates v51.1: the MOB-1 phone fix (v50.2x) put overflow-wrap:anywhere on every formula row's
  label and value, which lets the browser break inside a word or a number whenever the flex row is
  crowded — and the v51.x rows are longer. The fix keeps MOB-1's min-width:0 and changes the row
  contract: the label flexes and wraps at spaces (overflow-wrap:break-word); the value keeps its
  natural width (flex 0 0 auto, so a number is never squeezed) and a long value wraps at spaces
  inside a 70% cap, right-aligned; lone-value sentence rows and notes stay full width, left. A
  Playwright probe over 20 players x 3 widths (1380 / 400 / 375 px) that counts the text lines a
  numeric token occupies: 20 split rows before, 0 after; every remaining multi-line value is a
  sentence wrapping at spaces.

================================================================================
THE OTHER TOOLS (verify_calc.py, FAIL 0 WARN 1)
  INJURY MODULE     the v51.0 gates stand (im present and in [0,1] on all 2,080 priced records,
                    r == round(pc x pm x h x im), Hit% clean, no retired fields, ESPN-IL-but-
                    module-healthy hard check, GN_INJURY_MODULE == build.json) with the trajectory
                    gate now reading tj == tjp x Hit%(age+k) x inj.f[k]. New v51.1 gate on every
                    record with an asset term: p.im == inj.ia; ia reproduces from (1 + R) x V x
                    S x (1 - A_rec) x delta^defer to 1e-3; ia >= f[0]; every season before the
                    return season is a zero line; inj.im == f[0]; and, when build.json says v2.2,
                    every priced record carries ia. 0 broken. The 23 soft designation-vs-record
                    disagreements (data lag / unrostered) are the same WARN as v51.0.
  update_calc_weekly.py / apply_pace_v51.py: inj_factor(p, k) reads inj.f[k] so the next weekly
                    pace change keeps r = pc x pm x h x im and tj on the v2.2 factors.
  bump_build_v51_1.py: GN_BUILD, the .tc-sub line, the service-worker cache and build.json for a
                    point build, with update_calc_weekly's count guards.

================================================================================
WORKBOOK (resync_ceiling_workbook_v51.3.py)
  Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED_v51.3.xlsx, refreshed from the v51.2 workbook:
  1,412 rows, 2,778 cells changed, 187 Risk-Adj values moved, 749 rows under x1.00, 0 rows without
  a calculator record. No column and no meaning changes in v51.3; every figure downstream of S
  moves. 2_Org_Rankings recomputed: River Cats 53,522 still first, KC Gray Hotdogs 52,833 second,
  Kansas Sunflower Seeds 47,701 third. Sheets 3-12 re-stamped [NOT REFRESHED WK22]. The league-root
  UNIFIED file is not written (same rule as v50.21); the v51.3 workbook ships beside it and inside
  this build folder.

  The column layout, unchanged since v51.1 and repeated here so the sheet reads on its own:
  1,412 rows, 10,089 cells changed, 90 Risk-Adj values moved, 749 rows under x1.00, 0 rows
  without a calculator record. Column Q is re-headed "Injury Asset Mult" and
  carries ia (what Risk-Adj is priced on); column AI is "Inj Mult 2028 (yr 2)"; seven columns are
  appended (AL-AR): Season Line Mult 2027 (f[0]), Return Season, UCL Workload V, Deferral
  (seasons), Season Line RA 2027, Inj Mult 2029, Inj Mult 2030. Column S "Options Remaining"
  carries the same ledger as v51.0.
  (Those figures are the v51.1 sync's; the v51.3 numbers are stated above.)

================================================================================
SWEEP (sweep_v51_2.js — headless Chromium, both pages, Chart.js from vendor/chart.umd.js)
  168 checks PASS, 0 FAIL on index.html at 1380x900 and mobile.html at 400x860. Every build-specific
  expectation was repointed to v51.2 BY READING THE SHIPPED BOARD, not by typing figures from a note:
  Greene r 709 (was 753), asset x0.533 (was x0.565), lines 0 / 813 / 988; Ragans asset x0.563, 2027
  line x0.365, injury cost -44%; Crochet never-return risk 38% (was 27%); Keller x0.541; Steele
  x0.493; Ohtani x0.991. Two checks added, one per page: GN_EXIT_CALIB == 1.50.
  vendor/chart.umd.js (208,337 bytes, sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi)
  is byte-identical to the CDN build and matches the integrity attribute in both pages. It now lives
  in the build folder: the v51.1 copy was in a scratchpad and was lost, and neither sandbox can reach
  cdn.jsdelivr.net or the npm registry.
  (The v51.1 run, for the record: 166 checks PASS, 0 FAIL. sweep_v51.js was carried
  forward with the v2.2 expectations, 14 checks added.) What was driven, beyond the v51.0 list:
  build stamp "injury: Durability v2.2", the .tc-sub line, RAW 526.16 / GN_BUILD v51.2 /
  GN_INJURY_DELTA 0.90 / GN_UCL_WORKLOAD 0.85; in the browser's own arithmetic, r == round(pc x pm x
  h x im) on every priced record, im == inj.ia on all 2,080, gnInjFactor(p, k) == inj.f[k] on every
  record, no asset below its 2027 line, 8 players returning in 2028 and 34 carrying V; the value
  engine on Greene — 1-year window 753 (the asset), 2-year single-season 862 (the 2028 line),
  2-year cumulative 862 (0 + 862 over the 753 floor); the bust-risk-off view holding the year-0
  factor on every T3/T4 record under 1.00; Trade Desk with Ragans (row tag "Inj x0.60", legend
  "extreme, -40%"), Strider and Trout against Crochet, Jobe and Judge (injury card datasets equal
  to the RA each pick gives up, the untouched-pick subtitle); $ mode, 5-year cumulative, ROS '26,
  the 2026 time view, manager comparison and the EKG; the Inspector on Ragans (V row, "= 2027
  season line" x0.389, deferral 0.90^0.37, asset x0.600, the 2027 line 573 under the headline),
  Greene (header "Injury (asset): x0.565 (extreme)", "Return season 2028 — ... 2027 is a zero
  line", x0.85, "out all season", deferral x0.900, by-season 2027 x0.000 . 2028 x0.648 . 2029
  x0.830 . 2030 x0.897, the roll-off note naming the return season; never "Injury (asset):
  x0.000"), Brad Keller (x0.574, return season 2028), Steele (UCL revision, V on 2027, no
  deferral), Bautista, Crochet, Trout, Jobe, Griffin, Martin (flag), Woodruff, Helsley (rehab
  reset), Ohtani and Perez (untouched: no season-line row, no deferral row) — required strings
  present, stale strings absent, no undefined / NaN / null, the identity line equal to the header
  RA, six spine steps with step 6 reading "Durability v2.2 | x<asset>", the four-column flow
  tree on Ragans (V, the 2027 line, deferral 0.90^0.37, "= INJURY (asset)") and Greene ("return
  season 2028 (2027 out)", "2027 season line x0.000", deferral 0.90^1.00, x0.565); the Options
  tracker, its filter and provenance; the footer as-of line naming Durability v2.2. The only
  console error on either page is the Google Fonts stylesheet the sandbox cannot reach.
  Two presentation defects found in the phone screenshots and fixed before packaging: the V and
  deferral rows' long labels squeezed their values into "x0. / 85" and "x0.9 / 00" (labels
  shortened, the formula and the innings finding moved to a note under the asset row), and the
  by-season row's label wrapped to "Seaso / ns" (it is a full-width sentence now).

================================================================================
STILL NOT COVERED (carried from v51.0 unless struck here)
  - R phase-out INSIDE the return season (spec 3.8, R x (1 - a x w) as appearances accumulate)
    is still not coded; the return-season anchoring in this build settles WHICH season carries
    the rust, not how it fades within it. Code it before a returner has 15+ appearances on file.
  - The second-season half-weight (R/2) is a judgment call the data cannot yet measure (most
    UCL returners have not had a second season back); so is the 0.85 workload factor's
    application to the 2027 share of a mid-season return.
  - A player whose R comes from an older closed episode but whose open episode returns in 2028
    has that older rust pushed out with the return season (no such case on the board).
  - Evidence rule for IL pitchers with more than 15 appearances (30 rostered, 87 with the whole
    pool) — needs per-game logs.
  - Hit% base recalibration is a backtest gate item (spec 3.8); the back-test gate itself has not
    been run on v51.x.
  - 10 name/age bridge mismatches (Jake Rogers, Chadwick Tromp, Hayden Birdsong, Albert Suarez,
    Porter Hodge, Carlos Rodriguez, Orlando Ribalta, Josh Simpson, Jose Devers, Yunior Marte):
    treated as no record; a birth year on the board would settle them.
  - 16 MEDIUM news-facts entries (story text only) still await review; Martin and Stewart carry
    review flags.
  - Starting pitchers' appearances are G rather than GS in the rate multiplier (swingmen read low).
  - 23 players outside ESPN's 3,000-player pool hold last build's appearances and multiplier.
  - The 737 non-ESPN prospects carry forward unverified; 55 bridged T4 prospects with 2026 MLB
    cameos are still T4; 21 T3s at or past peak age await graduation (no birthdates on file).
  - HISTORY has a duplicate 2026-08-10 snapshot date, inherited from Week 19. Harmless.
  - season_roll_lambda_v50.21.py is staged but NOT run; it needs --apply --confirm-season-complete
    after the World Series.

================================================================================
THE v51.0 RECORD (unchanged; the full text is prev/README_v51.0.txt in the build folder)
  v51.0 (14 Sep 2026) replaced the v50 Hit% injury terms with the Durability v2.1 module, re-ran
  the pace multiplier on the whole 3,000-player pool, pulled the ESPN news for every injured
  player into injury_overrides.json (news_facts.py), and rebuilt the options ledger from the
  whole-season activity feed. Its README carries the per-step counts, the full-pool stats
  method, the news-facts extraction rules and traps, and the sweep of 152 checks.

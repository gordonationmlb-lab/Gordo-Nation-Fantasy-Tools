GORDO NATION TRADE CALCULATOR — v51.12  GNFV IS NO LONGER A CONSENSUS OF SCOUTS ALONE (2026-09-21)
  Same pull and data window as v51.0-v51.11: scoringPeriod 173, matchup period 22, week 22 data.
  F = 162/149 = 1.0872; September absorption 0.90. No weekly refresh ran.
  GN_BUILD v51.12, GN_DATA_THROUGH 2026-09-13.  RAW_PER_DOLLAR 535.77 -> 535.80.
  T4 risk-adjusted value +3.4%; 453 of 687 T4 records repriced, 234 left as they were.
  Acceptance: verify_calc.py FAIL 0 (WARN 1, the standing designation-lag warning).

  Methodology v15 records this build: §21 and §21.1 are new, and §11, §13, §15 and §19 amended.

================================================================================
1. WHAT CHANGED, IN ONE SENTENCE

  A prospect's value used to come entirely from scouting grades — the §7 curve turned a
  consensus FV into a ceiling and the §11 matrix turned tool grades into a bust. From v51.12
  a SECOND grader reads what he actually did in the minor leagues, and the two are blended
  slot by slot rather than one replacing the other.

================================================================================
2. PRODUCTION VALUE (PV)                          gn_pv_v51_12.py, §21

  Two surfaces, both fit on 11,379 prospect-seasons from 2019 and 2021-2023 carrying 2,244
  arrivals, hitters and pitchers in one frame but never in one pool:

    PV CEILING   what he is worth at peak IF he arrives, in Gordo Nation fantasy points,
                 fit as the 80th QUANTILE of best MLB season among the men who did arrive.
    PV ARRIVAL   the probability he reaches the majors at all, a calibrated logistic.

  Four inputs, all read off the line: percentile within (kind x level x season x role) on the
  RATE not the volume; age for level, struck on prospects only and clamped to [-5, +4]; the
  level; and playing time as a rank.

  THE QUANTILE IS NOT A DETAIL. A ceiling is an upper reach, not an expectation. A mean
  regression put only 55% of arrivals below their own "ceiling" and compressed the whole grid
  to FV 36-48. The 80th-quantile fit puts 80.0% below it and recovers FV 43-57.

  MEASURED, leave-one-anchor-year-out so nothing is scored on its own fit:
    PV                                    rho 0.4187   (hitters 0.4569, pitchers 0.3889)
    tool architecture, read charitably    rho 0.3179   (its ceiling replaced by PV's, so
                                                        only the Hit% swap is being tested)
    its level skeleton alone              rho 0.1777
  Of the 200 players PV ranks highest, 80.0% reached the majors and 47.0% posted a 600-point
  MLB season, against 19.7% and 5.8% for the cohort at large.

================================================================================
3. THE TWO-SLOT BLEND                             apply_pv_blend_v51_12.py, §21.1

  The two sides are good at OPPOSITE things, measured on the 453 board T4s carrying both:

                       10th      90th    spread
    tool ceiling        415      1080     2.60x    scouting separates CEILINGS
    PV ceiling          587       942     1.60x
    PV arrival         0.133     0.772    5.80x    production separates ARRIVAL
    scout 1 - bust     0.280     0.728    2.60x

  A box score cannot see the raw power or the fastball that makes a 70, so it compresses the
  top end. The bust matrix, floored at 0.20, cannot express the range of arrival risk that
  actually exists — which is what §11 already says about itself. Hence:

    CEILING SLOT    0.65 scouting + 0.35 production
    ARRIVAL SLOT    0.30 scouting + 0.70 production

  WHY PRODUCTION'S SHARE IS SO LARGE. The five outlets agree with each other at rho 0.656,
  which makes them worth 1.38 INDEPENDENT OPINIONS at a consensus reliability of 0.905 — the
  2nd through 5th source buy mostly redundancy. PV agrees with their consensus at 0.531, BELOW
  what they share with each other. PV is not a sixth opinion. It is a second one.

  THE WEIGHTS ARE CHOSEN, NOT FIT, AND THIS BUILD SAYS SO. The closed form needs three numbers
  and we have two: PV's correlation with realised value (0.419) and the two sides' correlation
  with each other (0.531). The third — how well a scouting grade predicts arrival — cannot be
  measured, because the project holds ONE vintage of grades (2026-09-17) and there is no way to
  score a 2019 grade against a 2019 player. Across every plausible setting of it PV earns 44%
  to 54% and the blend beats either side alone; 65/35 and 70/30 average into that band. Weekly
  GNFV vintage snapshots begin with this build so the weights can be fit in a season's time.

================================================================================
4. THREE THINGS TESTED AND REJECTED

  A PACE TERM FOR T4. Tried again on the new footing, at four absorptions and on both a raw
  and a level-neutral ratio. Every one made the fit worse. A prospect's year-over-year rate
  change correlates -0.035 with what he became, because a large jump usually means he repeated
  a level. The §13 gate stays closed — now for a measured reason rather than an argued one.

  A DURABILITY TERM. Minor-league availability does not carry forward: it predicts MLB
  availability at rho +0.075 for pitchers and -0.081 for hitters. Playing time DOES predict
  arrival at +0.263, but that is clubs giving innings to the men they mean to promote —
  opportunity, not health — so it enters as a FEATURE of both surfaces (+0.0164, CI [+0.0118,
  +0.0208]) and not as a multiplier outside them. §15.2's carve-out is untouched: a prospect
  with a known current injury still carries A_known and S, and nothing here could test that,
  because the minor-league pull holds no IL history.

  A PER-CELL RELIABILITY WEIGHT. PV's reliability runs from 0.513 at AA hitters to 0.032 at
  Rookie pitchers, which invites a weight that follows it. Tested, it LOSES at every setting —
  0.4324 against 0.3920 where the scouting side reads 0.25, 0.6345 against 0.6249 where it
  reads 0.55 — and the fixed arm was even given the oracle advantage of being chosen against
  the truth. The reason is familiar: a calibrated expectation already prices its own noise, so
  a reliability weight on top charges the same risk twice. It is the §9/§11 double-count in a
  new costume. Calibrate once, weight once.

================================================================================
5. WHERE PV ABSTAINS, AND WHY THAT IS NOT A WEIGHT

  Coverage is a hard rule. Where PV has no input its share goes to the scouts entirely:

    58   no 2026 minor-league line
    89   under 200 PA (hitters) or 150 BF (pitchers). Split-half reliability of a percentile
         is flat from 60 PA up (full-season rho 0.877-0.889) and only collapses below that,
         so the floor is about measurement, not taste.
    83   Rookie ball. PV reads rho 0.207 there for hitters and 0.032 for pitchers.
     4   fewer than 15 comparable cohort seasons. A fitted surface will draw anywhere; this
         is what stops it.
   453   repriced, covering 73% of T4 dollars.

  THE HONEST COST: PV is silent on exactly the players a dynasty league spends most on — the
  elite teenager with 120 plate appearances at a new level. Four of the nine rostered T4s
  abstain, including two of the most valuable prospects on the board.

================================================================================
6. TWO DEFECTS CAUGHT DURING THE BUILD

  THE QUADRATIC AGE TERM TURNED BACK UP AT THE FAR END. A 2019 AAA pitcher twenty years OLD
  for his level, sitting at the 31st percentile, priced out at 1,115 points; the whole
  +6-and-older band priced 37.8 against an actual 3.3. §4 sends a T4 over 30 to T5 so the live
  board never sees these men, but a surface must not lean on a rule outside itself.
  Age-for-level is clamped to [-5, +4], which costs 0.001 in rho and removes the tail.

  THE 2026 AGE BASELINE HAD TO BE STRUCK ON PROSPECTS ONLY. 64.8% of qualifying 2026 AAA
  pitchers have already debuted, and including them drags that level's median a full year
  older — which would have made every AAA arm read a year young against the scale the surfaces
  were trained on.

================================================================================
7. WHAT WAS DELIBERATELY NOT DECIDED

  THE T4 POOL'S MEAN ARRIVAL IS HELD WHERE IT WAS, at 0.4940, by a x1.1215 scale on the blend.
  PV is calibrated to a 19.7% cohort base rate while the scouting bust sits near 0.50, so
  blending raw would have marked the WHOLE prospect class down against the veterans. That is a
  separate ruling about how T4 stands against T1/T2/T3 and it is not taken here. This build
  redistributes inside the prospect pool and leaves its aggregate alone. The scale factor is
  printed by the apply script and recorded in pv_blend_report_2026-09-13.json.

  ALSO OUTSTANDING: PV is calibrated in rank but not in level — priced against realised value
  it runs a ratio near 0.59 and not flat across deciles (0.49 to 0.77). RAW re-floats so the
  level is harmless; the shape is not. An isotonic recalibration is the obvious next step and
  has not been done.

================================================================================
8. FILES

  gn_pv_v51_12.py             the two surfaces, the coverage rules, the season-line reducer.
                              numpy and pandas only — no scikit-learn at runtime.
  pv_fit_export.py            fits and exports the coefficients. Verified against the fitter
                              at 1.1e-16 on arrival and 0 on the ceiling.
  pv_model_v51_12.json        the exported surfaces. The board cannot move because a library
                              version moved underneath it.
  pv_cohort_v51_12.csv        11,379 prospect-seasons, the training record.
  pv_milb_2026.csv            the 2026 minor-league lines, both kinds, reduced.
  apply_pv_blend_v51_12.py    the blend, the re-float, the invariants.
  patch_v51_12.py             verify_calc.py learns the blend; the Inspector explains it.
  pv_blend_report_2026-09-13.json   what moved and by how much.

================================================================================
  Everything below this line is the v51.11 and v51.9 build notes, carried forward unchanged.
================================================================================


GORDO NATION TRADE CALCULATOR — v51.11  THE CEILING STOPS PAYING FOR THE INJURY TWICE (2026-09-21)
  Same pull and data window as v51.0-v51.9: scoringPeriod 173, matchup period 22, week 22 data.
  F = 162/149 = 1.0872; September absorption 0.90. No weekly refresh ran.
  Service worker: gordo-calc-v85-2026-09-13-v51.11.  GN_BUILD v51.11, GN_DATA_THROUGH 2026-09-13.
  RAW_PER_DOLLAR 526.03 -> 535.77.  Board RA 823,347 -> 836,943 (+1.7%); 470 records up, 26 down.
  Acceptance: verify_calc.py FAIL 0 (WARN 1, the standing designation-lag warning).

  Methodology v11 needs four amendments: 13.1 rebuilt, 14.1 added, the v51.1 asset headline
  superseded, and 20.31's "engage at the roll" given the code path it never had.

================================================================================
1. THE SS13.1 SEASON-ROLL CARRY IS REBUILT       season_roll_lambda_v51.11.py

  v51.10 widened the clamp to -0.55/+0.20 on a rank-correlation refit and the levels it
  produced were indefensible: pool RAW -12.4%, 178 of 483 rows cut by more than 30%, Aaron
  Judge -49%, Acuna -41%, Will Smith -45%, Sean Murphy -45%.

  WHY. pace = YTD x 162/team_games is VOLUME-based. A man who missed half the year annualises
  against the CALENDAR, not against his own playing time. Judge scored 526 points in 64 games
  -- 8.2 per game, better than Vlad's 7.2 -- and paced 572 against a Pure of 1,686: residual
  -66%. The residual is measured against the career PEAK, a maximum, so the pool median is
  -0.30 and 28% sit below -0.55. LAMBDA 1.00 with a -0.55 floor does not single out decliners;
  it drags most of the board to the floor.

  THE UNCOMFORTABLE PART. On rank the clamp is still better: rho 0.5431 against 0.4982 for the
  blend, n=2,463 pairs held out by year, bootstrap gap -0.0460 CI [-0.0602, -0.0311]. It is
  nevertheless a DURABILITY term wearing a ceiling's clothes, and that is measurable. Give both
  anchors the same availability term and the advantage evaporates -- clamp minus blend runs
  +0.0449 at k=0, +0.0021 at k=0.7, -0.0042 at k=1.0. On the 550 pairs who were FULLY AVAILABLE
  last year, where a markdown can only mean real decline, the blend edges it: 0.6644 against
  0.6630, both over peak's 0.6350. The clamp only wins where it re-prices injury, which SS15
  already prices in Hit% and SS12/SS20.15 prices again in the multiplier -- rate-based since
  v50.22, with its own confidence weight. The blend's multiplier reproduces that existing pm at
  Spearman 0.74, half the pool within 0.05, which is a validation and not a coincidence.

  WHAT REPLACES IT.
      av        = min(playing-time share, 1 - IL_days/186), floored at 0.15
      rate_form = pace / av                       a full season AT HIS OWN RATE
      w_eff     = W x av                          trusted in proportion to the evidence
      mult      = [(1-w_eff)*exp + w_eff*min(rate_form, exp*CAP_UP)] / exp
  W = 0.75, CAP_UP = 1.25 (a maximum lift of +18.75%, consistent with the retired CARRY_CAP of
  0.20 -- the ratchet owns upside). W is set on the fully-available players, where rho peaks at
  exactly 0.75 and falls after; on the full pool it keeps creeping to 1.00, but that extra is
  availability leaking back in.

  The docstring's "PENDING: games-played gate" is withdrawn. GP is in the feed (1,289 of 1,315
  carry-eligible records) and the blend uses it through av, so an IL-shortened season no longer
  reads as decline. --strict survives as an opt-in hard gate.

2. THE RATCHET AND THE FLOOR NOW FIRE AT THE ROLL

  55 rows were pinned at the career-peak cap. They are two defects, not one.

    14  banked to-date ALREADY exceeds the prior full-season peak -- Elvis Alvarado 1.44x,
        Zebby Matthews 1.28x, Dylan Crews 1.27x -- and SS20.17 says the ratchet "now fires for
        ALL surpassers". It had not. None carried eng.rch.

    41  regressed veterans at pm 1.27-1.50 whose banked total sits well BELOW their career
        peak. Kenley Jansen banked 489 against a 1,320 peak with Pure regressed to 363. SS19.6
        condition (1) is RIGHT not to fire. Their instrument is the SS20.12 recency floor, and
        SS20.31 says in terms: "the other 18 engage automatically at the roll when the
        multiplier resets, which is when they need it." No code path did that. banked_elsewhere()
        only ever SKIPPED players who already carried a RECENCY FLOOR note.

  Both are restored at the roll, as a MAX over the three routes rather than a precedence order.
  Both are upward instruments and neither may cut, which is what the SS19.6 crossover condition
  means; a strict order sent Randal Grichuk and Tyrone Taylor to a floor BELOW their carry and
  cut them 30%, the exact failure the condition exists to prevent.

  Dry run: routes carry 448 / ratchet 20 / floor 15. Eleven rows cut by more than 30% against
  240 under v51.10's clamp on the same rows. Kenley Jansen +66%, Sonny Gray +51% (the case
  SS20.31 names as the reason the floor's scope was extended to T1), George Springer +57%,
  Jake McCarthy +46%, Dylan Cease $3.65 -> $4.24.

  ALSO FIXED IN THE WRITE PATH. v51.10 rebuilt tj as tjp x Hit%(age+k) alone, dropping the
  injury factor the rest of the pipeline carries -- so the roll would have silently un-priced
  every injured player on the one run a year that rewrites the whole board. The invariant had
  the same hole and would not have caught it. Both now use the full identity.

3. THE INJURY ASSET MULTIPLIER IS NO LONGER A SCALAR PRODUCT     apply_injury_v2.py

  v51.1 built the asset headline as

      ia = (1 + R) x V x S x (1 - A_rec) x 0.90^defer

  while the module ALSO carried a correct year-by-year season line. Hunter Greene:

      f = [0.000, 0.6542, 0.8375, 0.9054, ...]     2027 / 2028 / 2029 / 2030+
      2028 = S x (1+R) x V = 0.9054 x 0.85 x 0.85 = 0.654      correct
      2029 = S x (1+R2)    = 0.9054 x 0.925       = 0.838      correct
      2030+= S                                     = 0.905     correct

  The product takes penalties that belong to 2028 alone -- the -15% rate hit and the x0.85
  workload, both of which this module's own note says apply "on the 2028 share he is back for"
  -- and charges them against all ten years, then adds a deferral discount to a year already
  zeroed. It over-penalised 509 of 2,080 records and under-penalised 5. Every one of the
  fourteen worst was UCL / Tommy John.

      ia = SUM_k f[k] w[k] / SUM_k w[k],   w[k] = tjp[k] x Hit%(age+k) x att(age,k)

  The share of a player's dynasty value the injury costs, with each year weighted by the value
  actually at risk in it. Checked against the league's own history -- 1,247 player-seasons with
  a healthy baseline and a measured follow-up -- a season lost to injury costs the CEILING 6.9%
  and total value 15.6%, or x0.863 / x0.782 with a survivorship correction. Tommy John read
  x0.526 on a +1/+2 window and x0.890 on +2/+4: the short window measures the missed year and
  the partial return, not the settled level, which is the same censoring shape that once taught
  the prospect model that low-level players never arrive.

  Hunter Greene $1.44 -> $1.72. Justin Martinez +45%, Cade Horton +28%, Pablo Lopez +26%,
  Cole Ragans +25%. Judge, Acuna, Soto and Witt move by 1% or less -- their ia was already
  0.98-0.99, and their drops were never the injury term.

4. SS14.1 ATTRITION                              gn_attrition_v51_11.py, hazard_fit.py

  tj[k] = tjp[k] x Hit%(age+k) x inj_factor(k) x att_factor(age, k)

  Nothing in the trajectory asked whether the player is still in the league in year k. Hit%
  answers "will he be healthy"; this answers "will he still be playing". Against 6,899
  anchor-to-year+k pairs from 2019-2026 (2020 is absent from the feed and is excluded, or every
  2019 anchor records a false non-survival at k=1):

      years out        1      2      3      4      5
      survival     0.905  0.795  0.701  0.612  0.520
      curve shape  0.922  0.954  0.987  1.041  1.028      <- on survivors

  The decline curve is ACCURATE, slightly conservative past year 3. All of the shortfall is
  players leaving the majors, and the undiscounted ten-year cumulative therefore over-projects
  realised five-year production by 29% (3,397 against 2,634 over 347 anchors with a full
  window). SS20.31's worry that lambda and a steeper curve would both correct the same measured
  gap does not apply: this is a third quantity.

  NOT A FLAT DISCOUNT. Attrition is violently age-dependent -- 0.770 five-year survival at 24
  against 0.110 at 34+, sevenfold. A flat 0.90^k over-charges the young by 8% and under-charges
  the old by 12% on the ten-year cumulative, a twenty-point spread in exactly the wrong
  direction for the commonest dynasty trade there is. The v51.1 deferral WAS that flat discount,
  charged to the injured alone; it is withdrawn and replaced by this, applied to everyone.

  THE SURFACE. Logistic in (k, age, k*age, k^2, age^2) inside the observed horizon k <= 5,
  which wins on leave-one-anchor-season-out MAE (0.2819 against 0.2850 for a smoothed empirical
  surface) and is 2.9x better than a chained one-year hazard on the age-band table. A chained
  hazard cannot express frailty and predicted 0.483 five-year survival for the 31-33 band
  against 0.308 observed, 0.327 against 0.110 for 34+. Beyond k=5 the survivor is AGED FORWARD
  with the one-year conditional survival at his attained age, scaled by a frailty factor of
  0.913 phased in over two years; conditional rates are capped at the attained-age hazard
  inside the horizon, which removes the k^2 term's upward turn (unconstrained it read 0.988
  survival in year 10 for a twenty-year-old against 0.882 in year 4). Monotone in k and, past
  peak age, in age: zero violations.

  SCOPE. SS14 trajectory only. RA is the one-year headline -- SS20 names YEARS=1 as in-season
  trade talk -- and att_factor(p, 0) is 1.0 for everyone by construction, so RA is untouched
  except through the injury weighting of item 3.

  THE FADE VIEW TOO. fadeAdjustedTj() rebuilds the trajectory client-side from tjp, so it
  carries att_factor as well. v51.0 found this once already with the injury term and left the
  reason in the code: the recomputed view must carry every factor the pipeline applies, "or
  the bust-risk-off toggle would silently release injury risk along with the scouting bust".
  The fade view is the PROSPECT view, where the ten-year horizon and the largest attrition
  exposure on the board both live.

================================================================================
DISCLOSURE.  Org RA: Dirty Spikes +2.9%, MidwestBears +2.1%, Balking Dead +1.7%, High Cheddar
  +1.2%, River Cats +1.1% (Hunter Greene), C-Town Liquors +1.0%, KC Gray Hotdogs +1.0%,
  Kansas Sunflower Seeds +1.0%. The commissioner's own club is tied for the smallest gain.

STILL OPEN.
  * pm reaches 1.50 while every banking instrument caps lower -- the carry at +18.75%, the
    floor at pace x 0.85 -- so the hottest overperformers lose value at every roll by design.
    The remaining large markdowns are all this: Luis Campusano (pm 1.500), Tyrone Taylor
    (1.448), Christian Encarnacion-Strand (1.411), Emilio Pagan (1.388). This is the "four
    mutually inconsistent trust weights" SS20.31 already deferred to the offseason. It wants a
    ruling, not a patch.
  * The attrition surface rests on one anchor season at the five-year horizon (n=347). The
    ranking gain over the undiscounted cumulative is +0.0200 with a 95% CI of [-0.0014,
    +0.0428] -- it straddles zero and is not claimed. The level correction and the age
    distribution are what the change rests on.
  * The Tommy John recovery figures rest on 12-17 players per window. The direction is
    consistent across all four windows; the level is soft.
  * Pitcher MLE, the in-season velocity trend, historical GNFV vintages and a longer prospect
    outcome window are all still open from the 20 September studies.

RUN ORDER TO REPRODUCE
  python3 hazard_fit.py                          # -> attrition_table_v51.11.json
  python3 patch_v51_11.py --apply                # apply_injury_v2 / update_calc_weekly / verify_calc
  python3 patch_fade_att_v51_11.py --apply       # calc/gn-app.js fade view
  python3 make_roll_v51_11.py --apply            # -> season_roll_lambda_v51.11.py
  python3 apply_injury_v2.py --apply             # re-price the board, re-float RAW
  python3 bump_build_v51_1.py v51.11
  python3 stamp.py --apply
  python3 verify_calc.py                         # expect FAIL 0, WARN 1
  python3 season_roll_lambda_v51.11.py calc/gn-app.js       # dry run only; the season is not over
GORDO NATION TRADE CALCULATOR — v51.9  NOTHING LEFT TO RELEASE (2026-09-20)
  Same pull and data window as v51.0-v51.8: scoringPeriod 173, matchup period 22 — the championship
  round — one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data. F = 162/149 = 1.0872;
  September absorption 0.90. No weekly refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v84-2026-09-13-v51.9.  GN_BUILD v51.9, GN_DATA_THROUGH 2026-09-13.

  v51.9 is a RENDER build like v51.8: one branch inside one section of the Player Inspector, and
  nothing else. PLAYERS is byte-identical to v51.7 and v51.8, and so is every one of the 7,048,645
  bytes of code outside renderInspector.
  Run with patch_ui_v51_9.py --apply and bump_build_v51_1.py v51.9, then stamp.py --apply.
  Acceptance: verify_calc.py FAIL 0 (WARN 1, the standing designation-lag warning), verify_v51_9.js
  PASS, and render_check_v51_9.js PASS — an A/B of the rendered panel HTML against v51.8.

================================================================================
WHAT CHANGED IN v51.9 — a release that releases nothing should not print a second ceiling

  HOW THIS STARTED. Spot-checking v51.8 through the live inspector at the commissioner's request.
  Emmet Sheehan's panel read

      = Peak RA (ceiling, risk-adjusted)     939
        Bust-risk-off release cap            no scouted ceiling on file — release uncapped
      = Peak RA (ceiling, bust-risk-off)     938   Y2, age 27

  — the released ceiling one point BELOW the risk-adjusted one, which reads as though releasing risk
  cost him value. Exactly the misreading v51.8 was built to remove, reappearing at the other end of
  the scale.

  WHY IT HAPPENED. Two things are true of Sheehan and of 51 others:

    * He has nothing to release. Of the 52, 49 are production-basis records, 2 vet and 1 tool; their
      mean matrix bust is 0.002 and the largest on the list is 0.10. The bust-risk-off view IS the
      risk-adjusted view for them.
    * The two figures are not the same statistic. `r` is peak-season RA at the player's true peak age
      (26 hitters / 27 pitchers); the grid's maximum is the best of the ten years actually listed.
      For a 26-year-old SP those land in different years, and both are rounded. Sheehan's unrounded
      gap is 0.88 of a point — the number was right and the presentation was wrong.

  WHAT THE PANEL DOES NOW. When the released peak does not come out ABOVE the risk-adjusted ceiling,
  the cap row, the released-peak row and the long note are replaced by one line — "there is nothing
  left to release on this record ... so the ten-year grid below is the same view as the chain above",
  with both figures and the reason they differ — and the ceiling row drops its ", risk-adjusted"
  qualifier. The panel is then the risk-adjusted panel plus one sentence. 52 of 1,116 prospect panels
  take this path; the other 1,064 are untouched.

  The released peak is now computed ONCE, in renderInspector's locals, and both the row label and the
  block below read it, so the label and the rows cannot disagree about which case the panel is in.

  THE GATE. verify_v51_9.js: PLAYERS byte-identical; 7,048,645 bytes outside renderInspector
  identical bar the GN_BUILD stamp; fadeAdjustedTj identical over 21,180 cells x 2 modes; the
  partition is 1,064 full / 52 suppressed, and the suppressed cohort is asserted to be the one with
  nothing to release (matrix bust max 0.100, mean 0.0019) and within 3 points of its own ceiling
  (worst -2); and the hoisted _relPeak reproduces the v51.8 inline computation for all 1,116.
  render_check_v51_9.js renders the SAME player in BOTH builds and diffs the section's innerHTML:
  571 panels, 519 byte-identical, 52 changed, 52/52 correct suppressed cases (cap row gone, second
  ceiling gone, qualifier dropped, explanatory line exactly once), no page errors in either build.

  WHAT DOES NOT CHANGE. Any valuation, and every panel that was showing a real release. No stored
  field, no trajectory, no dollar figure, no function outside the render template.

================================================================================
GORDO NATION TRADE CALCULATOR — v51.8  THE CEILING LINE FOLLOWS THE TOGGLE (2026-09-20)
  Same pull and data window as v51.0-v51.7: scoringPeriod 173, matchup period 22 — the championship
  round — one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data. F = 162/149 = 1.0872;
  September absorption 0.90. No weekly refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v83-2026-09-13-v51.8.  GN_BUILD v51.8, GN_DATA_THROUGH 2026-09-13.

  v51.8 is a RENDER build: three rows added to one section of the Player Inspector, and nothing
  else. PLAYERS is byte-identical to v51.7 and so is every one of the 7,048,653 bytes of code
  outside renderInspector.
  Run with patch_ui_v51_8.py --apply and bump_build_v51_1.py v51.8, then stamp.py --apply.
  Acceptance: verify_calc.py FAIL 0 (WARN 1, the standing designation-lag warning), verify_v51_8.js
  PASS, and render_check_v51_8.js PASS against the live DOM.

================================================================================
WHAT CHANGED IN v51.8 — two ceilings, both named, on the same panel

  HOW THIS STARTED. The complaint that survived v51.7. The inspector printed

      = Peak RA (ceiling)      664

  from the risk-ON chain, and three sections below it a ten-year grid that tops out at 1,488. The
  <h4> over the grid did say "bust-risk-off view", but nothing restated the ceiling in released
  units, so the only available reading of the panel was that the trajectory had broken its own
  ceiling. It had not. With bust risk off the curve climbs toward the UNdiscounted scouted ceiling,
  and the panel never showed that number anywhere.

  WHAT THE PANEL SAYS NOW. When FADE_MODE is on AND the player is T3/T4 — exactly the condition the
  grid switches basis on, asserted to be the same predicate — the existing row gains a qualifier
  and three rows follow it:

      = Peak RA (ceiling, risk-adjusted)                                             664
        Bust-risk-off release cap — scouted ceiling x pace (tc 1349 x sc 1.15 ...)   1551
      = Peak RA (ceiling, bust-risk-off)                       1488   Y7, age 26
      [note: which chain is which, and which one the grid below is on]

  Outside that condition the row is character-for-character what it always was, which the gate
  checks against a 193-player control sample of every other tier.

  HOW THE NUMBER IS DERIVED. It is not derived. The released peak is read off fadeAdjustedTj — the
  same function that fills the grid — and the maximum cell taken, so the ceiling and the grid
  cannot disagree by construction. The cap row names whichever term is actually binding: the
  scouted ceiling for 950 of the 977 capped prospects, the banked Pure for the 27 whose 19.6
  ratchet carried them past their scouting grade (gnReleaseCap floors the cap at pc — Dalton
  Rushing reads "banked Pure x pace (pc 1464 x pm 1.000; above the scouted 1463)"). The 139
  prospects with no eng.tc on file get "no scouted ceiling on file — release uncapped" rather than
  a fabricated bound.

  THE WIDEST GAPS THIS NOW MAKES LEGIBLE. Deep T4 arms, where the risk-adjusted number is almost
  all bust and the released number is almost all scouting grade:

      Chalniel Arias     22 T4   risk-adj   23   bust-risk-off  570 (Y6)   cap  597
      Marcus Phillips    22 T4   risk-adj   31   bust-risk-off  737 (Y6)   cap  784
      Thatcher Hurd      23 T4   risk-adj   33   bust-risk-off  730 (Y6)   cap  813
      Ethan Salas        20 T3   risk-adj  664   bust-risk-off 1488 (Y7)   cap 1551

  THE GATE. verify_v51_8.js: PLAYERS byte-identical; every byte outside renderInspector identical
  bar the GN_BUILD stamp; fadeAdjustedTj identical over 21,180 cells x 2 modes; the released peak
  is the max cell and sits under its printed cap for all 1,116 T3/T4 (tightest headroom 13.6 pts,
  Alexander Almonte); and the two predicates match. render_check_v51_8.js drives the real page in
  headless Chromium and cross-checks the DOM: 231 prospect panels and 193 controls, printed ceiling
  == grid max on every one, no page errors. Panels rendered both ways are in "Claude outputs/" as
  Ethan_Salas_Inspector_v51.8_risk-adjusted.png and _bust-risk-off.png.

  WHAT DOES NOT CHANGE. Any valuation. No stored field, no trajectory, no dollar figure, no
  function outside the render template. The $ row on this panel remains the risk-adjusted
  peak-season dollar, which is what it has always been and what the new note now says it is.

================================================================================
GORDO NATION TRADE CALCULATOR — v51.7  THE RELEASED HIT% AGES TOO (2026-09-20)
  Same pull and data window as v51.0-v51.6: scoringPeriod 173, matchup period 22 — the championship
  round — one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data. F = 162/149 = 1.0872;
  September absorption 0.90. No weekly refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v82-2026-09-13-v51.7.  GN_BUILD v51.7, GN_DATA_THROUGH 2026-09-13.

  v51.7 changes ONE EXPRESSION, in fadeAdjustedTj, and only in the bust-risk-off view. No valuation
  input moves: PLAYERS is byte-identical to v51.6, every stored ceiling, trajectory, Hit%, injury
  factor and dollar figure is untouched, and the risk-adjusted view is untouched.
  Run with patch_ui_v51_7.py --apply and bump_build_v51_1.py v51.7, then stamp.py --apply.
  Acceptance: verify_calc.py FAIL 0 (WARN 1, the standing designation-lag warning, unchanged from
  v51.6) and verify_v51_7.js PASS on all six invariants.

================================================================================
WHAT CHANGED IN v51.7 — the bust-risk-off view released the bust and then froze Hit% at today's age

  HOW THIS STARTED. The commissioner, 19 Sep, off the player inspector: Ethan Salas' ten-year
  trajectory shows years above his ceiling, is that a bug. It is not. Salas is a 20-year-old T3 at
  MLB Honeymoon whose stored ceiling is discounted twice over — pc 930 = tc 1349 x sc 1.15 x matur
  0.60 — and whose Hit% 0.714 carries the 0.42 matrix bust. With the Ceiling-Fade switch OFF his
  trajectory tops out at 664, exactly his Peak RA, and never exceeds it. With the switch ON, the
  Aug 25 ruling releases all three suppressors on the promotion ladder, so the curve climbs toward
  the UNdiscounted scouted ceiling — max(pc, tc x sc) x pm = 1551 — and peaks at 1488 in Y7, his
  age-26 year. That is the switch working. 1,064 of the board's 1,116 T3/T4 players read the same
  way, and a sweep of all of them found no release-cap breach anywhere. The complaint that does
  stand is presentational: the panel prints "Peak RA (ceiling)" from the risk-ON chain while the
  grid below it switches to the risk-OFF basis, and the two numbers are not comparable.

  THE DEFECT THE QUESTION TURNED UP. fadeAdjustedTj has two Hit% branches. The branch for a player
  with NO bust on file eases toward healthyBaseJS(yearAge, role) and therefore ages. The branch for
  a player WITH a bust on file — 977 of them, which is every prospect that matters — read

      hit = clamp(currentHit + base * (buste0 - busteK))

  and carried no age term at all. yearAge was computed six lines above and never used. So the view
  released the bust correctly and then held Hit% at today's age band for all ten years, while the
  engine's own risk-adjusted trajectory ages it on the healthy-base bands:

      Dalton Rushing  (25, C)    engine tj/tjp  0.795 -> 0.775 -> 0.755     fade-on  0.957 flat
      Parker Messick  (25, SP)   engine tj/tjp  0.940 -> 0.910 -> 0.880     fade-on  0.940 flat
      TJ Rumfield     (25, 3B)   engine tj/tjp  0.960 -> 0.940 -> 0.920     fade-on  0.960 flat

  This is the CALC FIX of 31 Aug — "trajectory Hit% now ages on the healthy-base bands instead of
  freezing at today's value" — landing in engine.py and never reaching this recomputation. The two
  views of the same player have disagreed about aging ever since, in one direction: the released
  view was always the generous one.

  THE FIX. Age the released Hit% by the ratio of the year's healthy base to today's, applied after
  the existing clamp:

      hitFull = clamp(currentHit + base * (buste0 - busteK))            <- unchanged
      ageBand = healthyBaseJS(yearAge, role) / healthyBaseJS(currentAge, role)
      hit     = max(0.20, hitFull * ageBand)

  Ratio form rather than healthyBaseJS(yearAge) * (1 - busteK) on purpose: at k = 0 the ratio is 1
  by construction, so the Current cell cannot move for any player, including the handful whose
  stored eng.base disagrees with the JS band table. healthyBaseJS is non-increasing in age, so
  ageBand <= 1 and the 0.96 clamp still binds. busteK <= buste0 and matFaded >= mat, so the released
  cell still dominates the risk-adjusted one: releasing risk does not subtract value.

  IS THE BAND RATIO THE RIGHT CORRECTION? Tested, not assumed. Reconstruct each stored tj[k] from
  tjp[k] two ways — Hit% frozen at today (what v51.6 did) and Hit% aged on the bands (what v51.7
  does) — with the injury roll-off divided out, since tj carries it and tjp does not. Over the
  8,748 trajectory cells of the 972 prospects with a bust on file:

      Hit% frozen at today   MAE 3.34 pts against the engine
      Hit% aged on the bands MAE 1.26 pts, median gap 0.51 pts

  A median gap of half a point is what two rounded integers produce. On the cleanest cases the match
  is exact: Messick's engine ratios read 0.9402 / 0.9103 / 0.8796 against SP bands 0.94 / 0.91 /
  0.88, and Sal Stewart, Cole Young and Konnor Griffin all step 0.96 -> 0.94 in the year they turn
  29. The engine ages on these bands; the fade path now ages on the same ones.

  WHAT IT COSTS. -1.03% on the 10-year bust-risk-off sum across the 977 affected records, -0.58%
  across the whole board, and it only ever took the number down — the old behaviour could only
  overstate. The correction is largest for players who cross the most bands inside ten years:

      Braxton Garrett    28 SP T3   2964 -> 2790   -5.9%
      Connor Noland      27 SP T4   3080 -> 2934   -4.7%
      Brandon White      27 SP T4   3883 -> 3705   -4.6%
      Triston McKenzie   28 RP T4   1241 -> 1186   -4.4%
      Brendan Beck       27 SP T3   3677 -> 3513   -4.4%
      Ethan Salas        20 C  T3  11741 -> 11715  -0.22%

  Salas, who raised it, barely moves: at 20 he crosses one band inside ten years, in Y10.

  THE GATE (verify_v51_7.js, in the build folder). Loads fadeAdjustedTj out of both builds and runs
  six invariants over all 2,118 players and 21,180 cells: year 0 identical in both modes; the
  risk-adjusted view untouched and still equal to the stored tj; no release-cap breach; the only
  change is Hit% and it is exactly the band ratio, with a no-bust player not moving at all; the
  released cell still dominating the risk-adjusted one (worst overhang 1.04 pts, on Edgardo
  Henriquez Y3, inside the 1.5-pt integer-rounding tolerance); and the band reconstruction beating
  the frozen one against the engine. PASS on all six.

  WHAT DOES NOT CHANGE. The risk-adjusted view, which reads the stored tj. Year 0 in both views.
  The release cap, the ladder clock, the peak clock, the bust release schedule, the maturation
  schedule, the injury module, the options ledger and every dollar figure on the board.

  STILL NOT COVERED. The panel still prints "Peak RA (ceiling)" from the risk-ON chain above a grid
  that may be on the risk-OFF basis, with nothing restating the ceiling in released units. That is
  the thing that actually prompted the question and it is a labelling change, not a valuation one.

================================================================================
GORDO NATION TRADE CALCULATOR — v51.6  THE PROSPECT BOARD, RE-READ (2026-09-17)
  Same pull and data window as v51.0-v51.5: scoringPeriod 173, matchup period 22 — the championship round —
  one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data. F = 162/149 = 1.0872; September absorption
  0.90. No weekly refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v81-2026-09-13-v51.6.  GN_BUILD v51.6, GN_DATA_THROUGH 2026-09-13.

  v51.6 is a VALUATION-INPUT build: every tool-basis prospect record (950 of 2,118) was re-read from the five outlets
  on 17 Sep 2026 — the first time any outlet has been read since the June 21 blend. GNFV, the tool ceiling, the
  tool-matrix bust, the level proximity and the maturation stage were all recomputed; 76 T4s with 2026 MLB time
  were graduated to T3 on the commissioner's call. The injury module, the pace multipliers, the options ledger
  and every non-prospect record are byte-identical to v51.5. RAW 525.39 -> 526.03.

  Run with bump_build_v51_1.py v51.6, apply_gnfv_v51_6.py --apply, write_readme_v51_6.py, stamp.py --apply and
  resync_ceiling_workbook_v51.6.py --apply. Acceptance: verify_calc.py FAIL 0 (WARN 1, the standing designation-lag
  warning), the invariant sweep inside apply_gnfv_v51_6.py (identity, tj, clean Hit%%, $, T4-with-MLB-games) ALL CLEAR,
  and the workbook's phase guard admitting exactly the tagged graduations.

================================================================================
WHAT CHANGED IN v51.6 — the five outlets, read again

  HOW THIS STARTED. The v51.5 README carried, under STILL NOT COVERED, "the 737 non-ESPN prospects carry forward
  unverified; 55 bridged T4 prospects with 2026 MLB cameos are still T4". Both dated from June 21: apply_gnfv7.py
  (v25) blended FanGraphs, MLB Pipeline, Just Baseball, Prospects Live and TJStats once, rebuild_gradeless.py (v29)
  read FanGraphs' tool grades once, and apply_prox74.py placed the top prospects on the level ladder from a June web
  check. Thirteen builds later a July draft class had arrived, FanGraphs had re-graded its whole board, Pipeline had
  re-ranked every system, three of the outlets had published new Top 100s and 76 of the board's T4s had played in
  the majors. The commissioner asked for the grades and the proximity to be re-read for every prospect.

  THE SOURCES (sources/ in the build folder, all captured through the commissioner's Chrome session on 17 Sep):
     fg_board_2026-09-17.json        FanGraphs The Board, "2026 Updated" — 1,371 rows, every team list: FV, ETA, present /
                                     future tool grades, current level, age, birth date. Read out of the page's own data.
     fg_graduates_2026-09-17.json    FanGraphs 2026 Graduates — 88 players who exhausted rookie eligibility this year, with
                                     the FV and grades FanGraphs left them on.
     mlbp_prospects_2026-09-17.json  MLB Pipeline Top 100 + thirty team Top 30s — 900 players: Overall grade, tool grades,
                                     ETA, current club and level, read from each page's embedded state.
     jb_top100_2026-09-17.json       Just Baseball Top 100 for 2026 (page dated 25 Aug): FV with the "+" tier edge, tool grades.
     pl_top100_2026-09-17.json       Prospects Live Pro Scouting Top 100 (17 Aug): OFP, level, ETA, future tool grades.
     tj_top100_2026-09-17.json       TJStats Top 100, post-draft update (1 Aug; player cards updated 17 Sep): FV, tools.
  Coverage on the board: FanGraphs anchors 949 of 950 records, Pipeline 517 (378 in June), Just Baseball 84, Prospects
  Live 84 (39 in June), TJStats 88. Source-count confidence: High (5) 67, Medium High 16, Medium 20, Medium Low 417, Low 430.

  THE BLEND IS THE JUNE BLEND. Same position-group weights (FG/MLBP/JB/PL/TJ — hitters 33/24/16/14/13, pitchers
  36/24/14/13/13, catchers 29/33/14/14/10), renormalised over the sources that grade each player; Pipeline on
  FanGraphs' scale as 0.92x + 3.2 (the June fit, n=378); TJStats' top end decompressed 50 + (x - 50) x 1.8 (their
  scale still stops at 60); FanGraphs' and Just Baseball's "+" read as +2. GNFV rose on 213 records, fell on 294 and
  held on 443. The ceiling follows GNFV exactly as v29 built it (cfv = GNFV + the de-risk premium, on the v28 scaled
  curve), and Pure moves by the RATIO of the recomputed tc x blend x maturation to the stored one, so a ratchet, a
  hand adjustment or a scarcity factor already inside a record's Pure rides through untouched.

  THE GRADES. 872 records were re-graded on the v13 tool matrix from FanGraphs' current future grades; 337 of them had
  never had grades on the record at all — their June bust was the 0.10 floor or an FV fallback, and they are where the
  largest moves in this build sit (A.J. Ewing 0.10 -> 0.41, Nick Yorke 0.31 -> 0.67, Carson Williams 0.27 -> 0.52). Across
  those with a June bust to compare (333) it moved -0.05 on average (190 down, 121 up, 22 flat), so the matrix is not systematically harsher than the fallback
  it replaces; it is specific. Records with no current FanGraphs grades keep their bust and say so in the note. The
  weak-command SP blend (CMD <= 45) is re-derived with the grades: it eases on Bubba Chandler (0.70 -> 0.86 — a 70
  fastball and a 70 changeup move the SP/RP/washout mix to 65/35/0) and tightens on Seth Hernandez (command 20/40,
  0.74) and Gage Jump (35/45, 0.80), which is most of what moved those three.

  LEVEL -> PROXIMITY -> LADDER. Each prospect's level is the highest he has reached in 2026 across FanGraphs (mlevel,
  else llevel), Pipeline's current club, Prospects Live's and TJStats' levels played, and ESPN MLB time; the stage the
  record already held is a floor (v50.20: a promotion never withdraws proximity credit, so a rehab assignment or a
  demotion listed today does not pull anyone down the ladder). Proximity bands as methodology 11 / apply_prox74:
  Rookie +0.25/+0.35, A and A+ +0.15/+0.20, AA -0.05/0.00, AAA and MLB -0.10/-0.05 (hitter/pitcher). 295 records changed
  proximity and 263 changed stage: A-or-below -> AA 109, AA -> AAA 64, A-or-below -> AAA 14, and the graduations below.
  72 records (all but three of them T3s who graduated before 2026) are on no current list; they keep the stage and
  proximity the record already carried.

  GRADUATIONS. A T4 is a player who has not played in the majors; 76 of them had — an ESPN-bridged record with 2026
  games or innings, or a name on FanGraphs' 2026 Graduates list. On the commissioner's call (17 Sep) they are T3 now,
  phased by the weekly's own rule on cumulative 2025 + 2026 FP (hitters 150 / 500, pitchers 250 / 750): 68 Honeymoon
  (x0.60, phase factor 0.80, Hit% cap 0.85), 8 Book (x0.80, phase factor 1.15). One is rostered — Josue De Paula,
  River Cats, 3 G -> MLB Honeymoon, $0.74 -> $1.11. The pace multiplier stays 1.00 for all of them (the §13 gate opens
  for a T3 only at Established, on the next weekly run). Every graduation carries a GRADUATION note on the record and
  the workbook's phase guard admits exactly those blank -> value flips.

  OFF THE BOARD. FanGraphs' team lists bottom out at 35+; a T4 who was on the June board and is on no FanGraphs list
  now has fallen below that, and reads FG 35 (the list floor): Jhonkensy Noel, Jacob Berry, Eli Whithold, Triston McKenzie, JP Wheat, Tink Hence, Landon Beidelschies.
  Three of the seven (McKenzie, Noel, Berry) were carrying a T4 tag they should never have had; the floor takes them to
  ~$0.10, which is where an unowned, unlisted free agent belongs, and the tag is left for the classification review.
  70 T3 tool-basis records graduated before 2026 and are on no 2026 list (Sasaki, Jobe, Rushing, Mayer, Dollander, ...);
  they keep their June FG, marked "carried" in the note and the consensus sheet.

  WHAT v51.6 DID TO THE BOARD. RAW 525.39 -> 526.03 (prospects rarely carry an ESPN id, so the $ anchor barely moves).
  Prospect RA 175,010 -> 192,758 (+10.1%); whole board 805,599 -> 823,347 (+2.2%). The rise is the graduations and the ladder climbs
  (a summer of promotions moved 187 prospects up a stage) landing mostly in the free-agent pool; the rostered prospect
  pool is DOWN on every club but Balking Dead and the Bears (Dirty Spikes flat), because rostered prospects are the graduated ones whose
  outside outlets stopped grading them (a graduate's GNFV collapses to FanGraphs alone) and whose FanGraphs grades came
  in below the June fallback.

  ROSTERED MOVERS ($, v51.5 -> v51.6; RA at the old and new RAW)
     A.J. Ewing             River Cats               CF  T3 Established     1130 ->   601   $2.15 -> $1.14 (-1.01)   GNFV 53 -> 47   bust 0.41   1 src
     Travis Bazzana         C-Town Liquors           2B  T3 Established     1077 ->   846   $2.05 -> $1.61 (-0.44)   GNFV 53 -> 50   bust 0.36   1 src
     Gage Jump              KC Gray Hotdogs          SP  T3 MLB Book         766 ->   555   $1.46 -> $1.06 (-0.40)   GNFV 52.4 -> 50   bust 0.23   1 src
     Bryce Eldridge         River Cats               DH  T3 Established     1023 ->   868   $1.95 -> $1.65 (-0.30)   GNFV 54.6 -> 55   bust 0.39   1 src
     Carter Jensen          Kansas Sunflower Seeds   C   T3 Established      946 ->   790   $1.80 -> $1.50 (-0.30)   GNFV 53.3 -> 50   bust 0.41   1 src
     Seth Hernandez         C-Town Liquors           SP  T4 A-or-below       328 ->   182   $0.62 -> $0.35 (-0.27)   GNFV 60.4 -> 60.7   bust 0.28   5 src
     Kevin McGonigle        C-Town Liquors           SS  T3                 1389 ->  1265   $2.64 -> $2.40 (-0.24)   GNFV 63 -> 60   bust 0.20   1 src
     Braden Montgomery      River Cats               CF  T3 MLB Book         651 ->   549   $1.24 -> $1.04 (-0.20)   GNFV - -> 50   bust 0.37   1 src
     Andrew Painter         C-Town Liquors           SP  T3 MLB Book         933 ->   837   $1.78 -> $1.59 (-0.19)   GNFV 53 -> 55   bust 0.24   1 src
     Hagen Smith            C-Town Liquors           SP  T3 MLB Book         471 ->   377   $0.90 -> $0.72 (-0.18)   GNFV 55.2 -> 49.7   bust 0.54   3 src
     Charlie Condon         C-Town Liquors           1B  T4 AAA              386 ->   289   $0.73 -> $0.55 (-0.18)   GNFV 57.4 -> 50   bust 0.52   4 src
     Samuel Basallo         River Cats               C   T3 Established     1501 ->  1421   $2.86 -> $2.70 (-0.16)   GNFV 63.2 -> 65   bust 0.34   1 src
     Ryan Sloan             C-Town Liquors           SP  T4 AA               580 ->   499   $1.10 -> $0.95 (-0.15)   GNFV 63.7 -> 58.9   bust 0.16   5 src
     Ethan Holliday         C-Town Liquors           SS  T4 A-or-below       218 ->   149   $0.41 -> $0.28 (-0.13)   GNFV 62.3 -> 50.9   bust 0.37   5 src
     Payton Tolle           KC Gray Hotdogs          SP  T3 Established     1335 ->  1273   $2.54 -> $2.42 (-0.12)   GNFV 56.3 -> 55   bust 0.10   1 src
     Kade Anderson          High Cheddar             SP  T3 MLB Honeymoon    915 ->   855   $1.74 -> $1.63 (-0.11)   GNFV 62.9 -> 60.7   bust 0.12   5 src
     ---
     Bubba Chandler         C-Town Liquors           SP  T3 Established     1008 ->  1259   $1.92 -> $2.39 (+0.47)   GNFV 59.5 -> 60   bust 0.10   1 src
     Josue De Paula         River Cats               LF  T3 MLB Honeymoon    390 ->   582   $0.74 -> $1.11 (+0.37)   GNFV 63.1 -> 57.8   bust 0.42   5 src
     Jarlin Susana          C-Town Liquors           SP  T4 AAA              307 ->   391   $0.58 -> $0.74 (+0.16)   GNFV 54.2 -> 53   bust 0.28   5 src
     Franklin Arias         River Cats               SS  T4 AAA              517 ->   602   $0.98 -> $1.14 (+0.16)   GNFV 61.4 -> 61   bust 0.27   5 src
     Carson Benge           Balking Dead             CF  T3 Established      899 ->   964   $1.71 -> $1.83 (+0.12)   GNFV 55.6 -> 55   bust 0.31   1 src
     Konnor Griffin         River Cats               SS  T3 MLB Book        1351 ->  1382   $2.57 -> $2.63 (+0.06)   GNFV 68.4 -> 70   bust 0.10   1 src
     Jesus Made             River Cats               SS  T4 AA               600 ->   632   $1.14 -> $1.20 (+0.06)   GNFV 63.8 -> 65.6   bust 0.10   5 src
     Eduardo Valencia       KC Gray Hotdogs          C   T3 MLB Book         356 ->   380   $0.68 -> $0.72 (+0.04)   GNFV 40.9 -> 42   bust 0.46   1 src
  FREE-AGENT MOVERS: up — Ty Johnson $0.21 -> $0.85, Owen Murphy $0.36 -> $0.97, Ethan Salas $0.65 -> $1.26, Kade Morris $0.27 -> $0.87, Demetrio Crisantes $0.31 -> $0.89, Harry Ford $0.34 -> $0.92, Santiago Suarez $0.25 -> $0.81, Matt Wilkinson $0.26 -> $0.74, Carlos Jorge $0.15 -> $0.60, Sean Keys $0.09 -> $0.53;
     down — Carson Williams $1.58 -> $0.78, Nick Yorke $1.10 -> $0.31, Owen Caissie $1.69 -> $0.91, Tyler Callihan $0.99 -> $0.31, Jacob Gonzalez $0.87 -> $0.27, Jimmy Crooks $1.32 -> $0.73, Henry Bolte $1.15 -> $0.60, Rhett Lowder $1.55 -> $1.01, Daniel Susac $0.89 -> $0.39, Miguel Ullola $0.85 -> $0.37.
  PROSPECT RA BY ORG (v51.5 -> v51.6):
     FA                       141,753 -> 161,138  $269.81 -> $306.33 (+36.52)
     C-Town Liquors            14,410 ->  13,757  $27.43 -> $26.15 (-1.27)
     River Cats                10,147 ->   9,516  $19.31 -> $18.09 (-1.22)
     KC Gray Hotdogs            4,001 ->   3,794  $7.62 -> $7.21 (-0.40)
     Balking Dead               1,751 ->   1,816  $3.33 -> $3.45 (+0.12)
     High Cheddar               1,067 ->   1,007  $2.03 -> $1.91 (-0.12)
     Kansas Sunflower Seeds       946 ->     790  $1.80 -> $1.50 (-0.30)
     MidwestBears                 710 ->     715  $1.35 -> $1.36 (+0.01)
     Dirty Spikes                 225 ->     225  $0.43 -> $0.43 (-0.00)
  2_Org_Rankings recomputed (River Cats 52,891 still first, KC Gray Hotdogs 52,626 second); C-Town Liquors 43,045 -> 42,392
  (-1.5%%, Bazzana -231 RA, McGonigle -124, Painter -96, Hagen Smith -94; Chandler +251) and River Cats 53,522 -> 52,891 (-1.2%%,
  Ewing -529) carry the largest rostered moves; Dirty Spikes is unchanged to the RA and the Bears move +5.

  THE GRADUATIONS (T4 -> T3; G / IP are 2026 MLB; cum FP is 2025 + 2026):
     Luis Lara              FA (MIL)       CF  G 49  IP 0.0    cum 270  -> Book      (AAA -> MLB Book)
     Brett Bateman          FA (CHC)       CF  G 31  IP 0.0    cum 239  -> Book      (AAA -> MLB Book)
     Gabriel Hughes         FA (COL)       SP  G 13  IP 59.3   cum 223  -> Honeymoon (AAA -> MLB Honeymoon)
     Abimelec Ortiz         FA (WSH)       1B  G 37  IP 0.0    cum 197  -> Book      (AAA -> MLB Book)
     Trent Harris           FA (SF)        RP  G 15  IP 17.0   cum 192  -> Honeymoon (AAA -> MLB Honeymoon)
     Justin Hagenman        FA (NYM)       SP  G 2   IP 4.0    cum 188  -> Honeymoon (AAA -> MLB Honeymoon)
     Tyler Schweitzer       FA (CWS)       RP  G 18  IP 37.3   cum 182  -> Honeymoon (AAA -> MLB Honeymoon)
     Kaelen Culpepper       FA (MIN)       SS  G 30  IP 0.0    cum 181  -> Book      (AAA -> MLB Book)
     Tommy White            FA (ATH)       3B  G 44  IP 0.0    cum 176  -> Book      (AA -> MLB Book)
     Harry Ford             FA (WSH)       C   G 30  IP 0.0    cum 166  -> Book      (A-or-below -> MLB Book)
     Riley Cornelio         FA (WSH)       RP  G 14  IP 27.7   cum 164  -> Honeymoon (AAA -> MLB Honeymoon)
     Mitch Bratt            FA (ARI)       SP  G 10  IP 44.0   cum 158  -> Honeymoon (AA -> MLB Honeymoon)
     Hector Rodriguez       FA (CIN)       RF  G 31  IP 0.0    cum 155  -> Book      (AAA -> MLB Book)
     Angel Genao            FA (CLE)       SS  G 32  IP 0.0    cum 153  -> Book      (AAA -> MLB Book)
     Mason Adams            FA (CWS)       SP  G 4   IP 18.7   cum 147  -> Honeymoon (AAA -> MLB Honeymoon)
     George Klassen         FA (LAA)       SP  G 6   IP 27.0   cum 143  -> Honeymoon (AAA -> MLB Honeymoon)
     Alex McFarlane         FA (PHI)       RP  G 15  IP 14.7   cum 141  -> Honeymoon (AA -> MLB Honeymoon)
     Joshua Kuroda-Grauer   FA (ATH)       2B  G 16  IP 0.0    cum 116  -> Honeymoon (AAA -> MLB Honeymoon)
     Ethan Pecko            FA             SP  G 5   IP 23.0   cum 108  -> Honeymoon (A-or-below -> MLB Honeymoon)
     Jose Cabrera           FA (ARI)       RP  G 7   IP 27.0   cum 106  -> Honeymoon (AA -> MLB Honeymoon)
     Zac Veen               FA (COL)       LF  G 26  IP 0.0    cum 105  -> Honeymoon (A-or-below -> MLB Honeymoon)
     Kahlil Watson          FA (CLE)       CF  G 27  IP 0.0    cum 84   -> Honeymoon (AAA -> MLB Honeymoon)
     Yunior Marte           FA (SF)        SP  G 3   IP 14.7   cum 84   -> Honeymoon (AA -> MLB Honeymoon)
     Matt Wilkinson         FA (CLE)       SP  G 6   IP 19.7   cum 82   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Kohl Drake             FA (ARI)       SP  G 5   IP 20.7   cum 77   -> Honeymoon (AAA -> MLB Honeymoon)
     Drew Cavanaugh         FA (SF)        C   G 50  IP 0.0    cum 77   -> Honeymoon (AAA -> MLB Honeymoon)
     John Peck              FA (DET)       SS  G 10  IP 0.0    cum 74   -> Honeymoon (AA -> MLB Honeymoon)
     Kevin Alcantara        FA (CHC)       CF  G 20  IP 0.0    cum 73   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Andrew Sears           FA (DET)       RP  G 4   IP 16.7   cum 73   -> Honeymoon (AA -> MLB Honeymoon)
     Jackson Kent           FA (WSH)       SP  G 6   IP 27.3   cum 67   -> Honeymoon (AA -> MLB Honeymoon)
     Lazaro Montes          FA (SEA)       RF  G 11  IP 0.0    cum 60   -> Honeymoon (AA -> MLB Honeymoon)
     Sean Keys              FA (TOR)       3B  G 17  IP 0.0    cum 60   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Ricky Tiedemann        FA (TOR)       SP  G 5   IP 6.0    cum 56   -> Honeymoon (AAA -> MLB Honeymoon)
     Carson Palmquist       FA (COL)       RP  G 11  IP 16.3   cum 56   -> Honeymoon (AAA -> MLB Honeymoon)
     Cooper Hjerpe          FA (STL)       RP  G 2   IP 5.0    cum 53   -> Honeymoon (AA -> MLB Honeymoon)
     Brock Rodden           FA (SEA)       2B  G 22  IP 0.0    cum 52   -> Honeymoon (AA -> MLB Honeymoon)
     Khristian Curtis       FA (PIT)       SP  G 4   IP 14.0   cum 49   -> Honeymoon (AA -> MLB Honeymoon)
     Michael Arroyo         FA (SEA)       2B  G 4   IP 0.0    cum 46   -> Honeymoon (AA -> MLB Honeymoon)
     Josue De Paula         River Cats     LF  G 3   IP 0.0    cum 41   -> Honeymoon (AA -> MLB Honeymoon)
     Owen Murphy            FA (ATL)       SP  G 3   IP 6.7    cum 38   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Connor Thomas          FA (ATL)       RP  G 13  IP 17.3   cum 36   -> Honeymoon (AAA -> MLB Honeymoon)
     Marco Raya             FA (MIN)       RP  G 3   IP 6.0    cum 31   -> Honeymoon (AAA -> MLB Honeymoon)
     Austin Peterson        FA (CLE)       SP  G 1   IP 2.0    cum 28   -> Honeymoon (AAA -> MLB Honeymoon)
     Nick Morabito          FA (NYM)       CF  G 12  IP 0.0    cum 28   -> Honeymoon (AA -> MLB Honeymoon)
     Ty Johnson             FA (TB)        SP  G 3   IP 2.3    cum 27   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Nate Furman            FA (SF)        2B  G 19  IP 0.0    cum 27   -> Honeymoon (AAA -> MLB Honeymoon)
     Luis De León           FA (BAL)       SP  G 5   IP 5.3    cum 24   -> Honeymoon (AA -> MLB Honeymoon)
     Jared Serna            FA (MIA)       SS  G 6   IP 0.0    cum 20   -> Honeymoon (AAA -> MLB Honeymoon)
     Blake Walston          FA (ARI)       SP  G 2   IP 3.0    cum 14   -> Honeymoon (AAA -> MLB Honeymoon)
     Luis Perales           FA (WSH)       RP  G 4   IP 7.0    cum 13   -> Honeymoon (AAA -> MLB Honeymoon)
     Sean Sullivan          FA (COL)       RP  G 3   IP 15.3   cum 11   -> Honeymoon (AA -> MLB Honeymoon)
     James Triantos         FA (CHC)       2B  G 5   IP 0.0    cum 10   -> Honeymoon (AAA -> MLB Honeymoon)
     Brendan Beck           FA (NYY)       SP  G 3   IP 7.7    cum 7    -> Honeymoon (AAA -> MLB Honeymoon)
     Dylan Ross             FA (NYM)       RP  G 1   IP 1.0    cum 6    -> Honeymoon (AAA -> MLB Honeymoon)
     Braxton Roxby          FA (SF)        RP  G 2   IP 2.0    cum 6    -> Honeymoon (AAA -> MLB Honeymoon)
     Blake Burkhalter       FA (ATL)       RP  G 1   IP 1.0    cum 2    -> Honeymoon (AAA -> MLB Honeymoon)
     Winston Santos         FA (TEX)       SP  G 1   IP 2.0    cum 1    -> Honeymoon (AAA -> MLB Honeymoon)
     Robby Snelling         FA (MIA)       SP  G 1   IP 5.0    cum 0    -> Honeymoon (AAA -> MLB Honeymoon)
     Cade Winquest          FA (NYY)       RP  G 1   IP 0.0    cum 0    -> Honeymoon (AA -> MLB Honeymoon)
     Ben Ross               FA (MIN)       SS  G 3   IP 0.0    cum -1   -> Honeymoon (AAA -> MLB Honeymoon)
     BJ Murray              FA (CHC)       3B  G 6   IP 0.0    cum -2   -> Honeymoon (AAA -> MLB Honeymoon)
     Brody Hopkins          FA (TB)        SP  G 1   IP 1.0    cum -3   -> Honeymoon (AAA -> MLB Honeymoon)
     Kyler Fedko            FA (MIN)       RF  G 10  IP 0.0    cum -3   -> Honeymoon (AAA -> MLB Honeymoon)
     Ethan Salas            FA (SD)        C   G 7   IP 0.0    cum -6   -> Honeymoon (AA -> MLB Honeymoon)
     Trei Cruz              FA             SS  G 2   IP 0.0    cum -6   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Emiliano Teodo         FA (TEX)       RP  G 1   IP 1.7    cum -6   -> Honeymoon (AAA -> MLB Honeymoon)
     Carlos Jorge           FA (CIN)       CF  G 6   IP 0.0    cum -9   -> Honeymoon (A-or-below -> MLB Honeymoon)
     Tanner McDougal        FA (CWS)       SP  G 1   IP 0.3    cum -12  -> Honeymoon (AA -> MLB Honeymoon)
     Cooper Ingle           FA (CLE)       C   G 7   IP 0.0    cum -16  -> Honeymoon (AAA -> MLB Honeymoon)
     Yilber Díaz            FA             RP  G 5   IP 6.0    cum -22  -> Honeymoon (A-or-below -> MLB Honeymoon)
     Braxton Garrett        FA (MIA)       SP  G 2   IP 4.3    cum -22  -> Honeymoon (A-or-below -> MLB Honeymoon)
     Kade Morris            FA (ATH)       SP  G 6   IP 17.3   cum -27  -> Honeymoon (A-or-below -> MLB Honeymoon)
     Hancel Rincon          FA (STL)       SP  G 2   IP 1.3    cum -29  -> Honeymoon (AA -> MLB Honeymoon)
     Wilkin Ramos           FA (SF)        RP  G 2   IP 2.0    cum -29  -> Honeymoon (AAA -> MLB Honeymoon)
     Jose Corniell          FA (TEX)       SP  G 2   IP 4.3    cum -39  -> Honeymoon (AAA -> MLB Honeymoon)
     Jedixson Paez          FA (CWS)       SP  G 4   IP 6.7    cum -60  -> Honeymoon (A-or-below -> MLB Honeymoon)

  WHAT IS ON EACH RECORD NOW. eng.fg_fv / mlbp_fv / jb_fv / pl_fv / tj_fv are the outlets' RAW grades; eng.gnfv, nsrc,
  conf, fv (= round GNFV), cfv and tc the blend and the ceiling; eng.fg_src says board / graduates / off-board floor /
  carried; eng.lvl and lvl_src the level and where it came from; eng.eta (FanGraphs, else Pipeline), fg_rank, fg_org_rank,
  fg_trend, mlbp_rank / mlbp_eta / mlbp_lvl, jb_rank, pl_rank, tj_rank the outlets' own placements; eng.grades the
  current FanGraphs tool grades with grades_asof; eng.bd the FanGraphs birth date. Nothing in the calculator UI reads a
  new field yet — the Inspector's tool-ceiling, bust and proximity rows show the refreshed values through the fields
  they already read, and the GNFV REFRESH note on every record carries the sources and the before/after.

================================================================================
THE WORKBOOK (resync_ceiling_workbook_v51.6.py --apply, from the v51.3 workbook)
  1_Player_Inputs refreshed in place (1,412 rows, 204 Risk-Adj moved) with the tier and phase of the graduates written;
  2_Org_Rankings recomputed. 12_Prospect_Consensus_FV is REBUILT for the 17 Sep vintage — all 950 tool-basis records,
  the five raw outlet grades, GNFV with the June 21 GNFV beside it, the v51.5 $ and the delta, tier / stage, level, ETA,
  bust, proximity, ceiling, Pure, Hit%, Risk-Adj and the FG source. 7_Prospect_Rankings is REBUILT: Top 100 by Pure
  ceiling (T4 + T3 Book/Honeymoon) and the per-level Top 25s, with GNFV / sources / bust / level in the note column.
  Every other sheet keeps its [NOT REFRESHED WK22] banner. Written as Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED_v51.6.xlsx
  at the league root and in this build folder; the root UNIFIED.xlsx is not touched.

================================================================================
THE OTHER TOOLS
  verify_calc.py       FAIL 0, WARN 1 — the standing 23 designation-vs-module soft disagreements. Every prospect record
                       reproduces r = round(pc x pm x h x im), tj = tjp x Hit%(age+k) x f[k], the clean Hit% assembly and
                       d = r / RAW; HISTORY's 2026-09-13 snapshot restated with the refreshed r; GNDAILY.raw re-stamped.
  apply_gnfv_v51_6.py  dry run prints the whole report; --apply refuses to write on any invariant violation. Writes
                       gnfv_report_2026-09-17.json (movers, graduations, off-board, carried, no-level, age gaps, orgs)
                       and gnfv_consensus_2026-09-17.json (the table the workbook sheet is built from).
  stamp.py             two fixes. (1) The pages' as-of line had grown four stray closing parentheses since v51.1 — the
                       editorial clause carried "(&times;1.50)", the pattern stopped at its ')' and left the outer one
                       behind on every stamp, so v51.5 shipped "...(&times;1.50)))))". The pattern now matches to the
                       next tag and writes one paren back. (2) The README identity line is dated by the BUILD date
                       (build.json 'built', new), as v51.3-v51.5 wrote it by hand, not by the pull date; and only
                       this build's card (above the first rule) is stamped, since the earlier builds' cards below it
                       carry lines of the same shape.
  package.py --apply   the flat app zip and the build zip, stamps re-read from the archive.

================================================================================
STILL NOT COVERED (carried from v51.5 unless struck here)
  - STRUCK: "737 non-ESPN prospects carry forward unverified" and "55 bridged T4 prospects with 2026 MLB cameos are
    still T4" — every tool-basis record was re-read on 17 Sep and the 76 with MLB time are T3.
  - NEW: the 2026 draft class and the summer's new international signings are NOT on the board. FanGraphs' list carries
    54 rows with no player id yet, and the outlets' Top 100s name Roch Cholowsky (FG #18, 55 FV), Grady Emerson (#14),
    Vahn Lackey (#13), Jackson Flora, Eric Booth Jr., Tyler Bell, Drew Burress, Taitn Gray, Cooper Flemming and others
    who have no calculator record. Adding them is a build_prospects.py pass with an ESPN-id bridge, not a refresh.
  - NEW: ages. FanGraphs' decimal current age runs a year or more ahead of the board's integer a on 117 records —
    birthdays passed since the June AGE FIX, or a season-age convention; the FanGraphs birth date is now stored on
    eng.bd for the fix, which touches the growth ramp and is a separate step.
  - NEW: a graduate's GNFV is FanGraphs alone once the prospect outlets stop listing him (Basallo, Griffin, Tolle, ...
    all read 1 src / Low). That is the data, not a defect, but the confidence column should be read that way.
  - NEW: three T4-tagged veterans (Triston McKenzie, Jhonkensy Noel, Jacob Berry) sit at the FG floor; the tag is wrong,
    not the value — Player_Classifications_Review.xlsx is where that gets fixed.
  - R phase-out INSIDE the return season (spec 3.8) is still not coded; the second-season half-weight and the 0.85
    workload factor on a mid-season return remain judgement calls; the Hit% base recalibration is a back-test gate item.
  - Evidence rule for IL pitchers with more than 15 appearances (per-game logs); starting pitchers' appearances are G
    rather than GS in the rate multiplier; 23 players outside ESPN's 3,000-player pool hold last build's appearances.
  - 10 name/age bridge mismatches (Jake Rogers, Chadwick Tromp, Hayden Birdsong, Albert Suarez, Porter Hodge, Carlos
    Rodriguez, Orlando Ribalta, Josh Simpson, Jose Devers, Yunior Marte) treated as no record.
  - 16 MEDIUM news-facts entries still await review; Martin and Stewart carry review flags.
  - season_roll_lambda_v50.21.py is staged but NOT run; it needs --apply --confirm-season-complete after the World Series.

================================================================================
GORDO NATION TRADE CALCULATOR — v51.5  A RELEASE IS NOT A DEMOTION (2026-09-16)
  Same pull and data window as v51.0-v51.4. Week 22 data. F = 1.0872; absorption 0.90. No weekly
  refresh ran. Methodology v11 stands.
  Service worker: gordo-calc-v80-2026-09-13-v51.5.  GN_BUILD v51.5, GN_DATA_THROUGH 2026-09-13.

  v51.5 changes THREE STRINGS and one status branch. No valuation input, no option burn and no
  ledger entry moves: OPTIONS_DATA is byte-identical to v51.4. Run with patch_ui_v51_5.py --apply
  and bump_build_v51_1.py v51.5. Acceptance: verify_calc.py FAIL 0, and no Rule 5 player reading
  ILLEGAL DEMOTION.

================================================================================
WHAT CHANGED IN v51.5 — the Rule 5 list was calling a legal release an illegal demotion

  v51.4 taught the RECORD CARD that a draftee can revert to ordinary property. It did not teach
  the RULE 5 FILTER LIST, which computes its own status from the roster and has no `reverted`
  branch. It saw Dingler on his drafting organisation's AAA club and printed
  "⚠ ILLEGAL DEMOTION (AAA roster) — Midwest Bears may recapture". Both halves are wrong.

  A DEMOTION is a move from the drafting manager's MLB roster to a AAA roster. Art. V(b)(4)(B)(iii)
  and (C) prohibit TRADING or DEMOTING a draftee and leave exactly one transaction open: release to
  waivers. High Cheddar released him Sep 7 — the permitted door. hicheddar AAA acquired him from
  the pool Sep 10, a separate transaction three days later, by which time he was an ordinary
  player. Calling that a demotion describes a move that never happened.

  "MIDWEST BEARS MAY RECAPTURE" is equally stale. Advisory Opinion 2026-R5-02, Holding 3:
  declination or expiry of the two-day window extinguishes every reclamation right, in-season and
  preseason alike. Their window closed Sep 9. Offering a recapture the rules no longer grant is
  worse than printing nothing.

  WHAT DOES NOT CHANGE: the option. VI(b)(3) asks one question — what was the most-immediate prior
  roster status — and the answer is MLB. Time in the free-agent pool has no bearing on it, and
  V(b)(4)(C)(iii) says in terms that no exception to VI(b)(3) is granted to a reverted player. The
  Sep 10 burn stands; the ledger is untouched.

  THE THIRD EXIT, now stated. The list's standing note described two ways off the MLB roster —
  recapture on an attempted illegal demotion, or a waiver claim by the original manager — and
  omitted the one that actually occurred: the original manager passes, the window expires, the
  player clears, and he reverts to ordinary property under (C)(iii), keeper-eligible on ordinary
  terms under Holding 5 even if the drafting organisation signs him back. The note says so now,
  and says that such a signing still charges an option.

  The record card's note for Dingler is restated in the same terms: it leads with "This was a
  RELEASE, not a demotion," and it still marks the commissioner's determination as pending rather
  than ruling on the keeper tag.

================================================================================
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

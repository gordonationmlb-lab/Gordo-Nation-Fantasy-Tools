GORDO NATION TRADE CALCULATOR — v51.1  DURABILITY v2.2 POINT BUILD (2026-09-14)
  Same pull and data window as v51.0: scoringPeriod 173, matchup period 22 — the championship
  round, SP167-180 — one week in (SP167-173 complete, Sep 7 - Sep 13). Week 22 data.
  F = 162/149 = 1.0872; September absorption 0.90. No weekly refresh ran; this is a framework
  point build on the injury module (Durability v2.1 -> v2.2, commissioner's decisions of 15 Sep
  2026 after the Hunter Greene case). Methodology v11 otherwise stands.
  Service worker: gordo-calc-v76-2026-09-13-v51.1.  GN_BUILD v51.1, GN_DATA_THROUGH 2026-09-13.

  Run with bump_build_v51_1.py (the identity lines a point build has no refresh to write), then
  apply_injury_v2.py, patch_ui_v51_1.py (once — it refuses a second run), patch_css_v51_1.py
  (the Inspector wrapping hotfix, idempotent), stamp.py and resync_ceiling_workbook_v51.1.py.
  Acceptance: verify_calc.py, FAIL 0. The weekly template
  (update_calc_weekly.py, apply_pace_v51.py, news_facts.py, update_options.py) is carried
  forward with its injury helpers updated to the v2.2 fields, ready for the next pull.

================================================================================
WHAT CHANGED — two rules, both stated on every record they touch
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

  WHAT IT DID TO THE BOARD. RAW 527.29 -> 530.98 (+0.7%); board RA 804,530 -> 813,667 (+1.1%).
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
  ORG RA: River Cats 53,121 -> 54,181 (+2.0%), Dirty Spikes 45,396 -> 46,025 (+1.4%), Balking
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
WORKBOOK (resync_ceiling_workbook_v51.1.py)
  Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED_v51.1.xlsx, refreshed from the v51.0 workbook:
  1,412 rows, 10,089 cells changed, 90 Risk-Adj values moved, 749 rows under x1.00, 0 rows
  without a calculator record. Column Q is re-headed "Injury Asset Mult" and
  carries ia (what Risk-Adj is priced on); column AI is "Inj Mult 2028 (yr 2)"; seven columns are
  appended (AL-AR): Season Line Mult 2027 (f[0]), Return Season, UCL Workload V, Deferral
  (seasons), Season Line RA 2027, Inj Mult 2029, Inj Mult 2030. Column S "Options Remaining"
  carries the same ledger as v51.0.
  2_Org_Rankings recomputed (River Cats 54,181 still first, KC Gray Hotdogs 52,844 second).
  Sheets 3-12 re-stamped [NOT REFRESHED WK22]. The league-root UNIFIED file is not written (same
  rule as v50.21); the v51.1 workbook ships beside it and inside this build folder.

================================================================================
SWEEP (sweep_v51_1.js — headless Chromium, both pages, Chart.js from the byte-identical local copy)
  166 checks PASS, 0 FAIL on index.html at 1380x900 and mobile.html at 400x860 (sweep_v51.js carried
  forward with the v2.2 expectations, 14 checks added). What was driven, beyond the v51.0 list:
  build stamp "injury: Durability v2.2", the .tc-sub line, RAW 530.98 / GN_BUILD v51.1 /
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

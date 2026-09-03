GORDO NATION TRADE CALCULATOR — v50.20  AUDIT-FIX BUILD (2026-09-03)
  Same data window as v50.18/v50.19 (Week 21: MP21 = SP153-159, Aug 24-30 complete; F = 162/137.3 = 1.1799;
  August absorption 0.80). This build applies the 24 findings of the Sep 3 audit
  (Calculator_v50.19_Methodology_v10_Audit_2026-09-03.docx) — every one a case where the rule already written in
  the methodology was not what the build did. No framework change. Methodology v11 ships alongside.
  Service worker: gordo-calc-v69-2026-09-03.  GN_BUILD v50.20, GN_DATA_THROUGH 2026-08-30.

================================================================================
ENGINE DATA (patch_data_v50_20.py, report in patch_report.json)   — 545 records touched, 393 repriced
  RAW_PER_DOLLAR 501.35 -> 497.64 (anchor pool 1,174 -> 1,376 eid-bearing r>0 after the bridge)
  Board RA 728,759 -> 762,833 (+34,074, +$68.5): 357 up, 36 down. Nine invariants: 0 violations.

  1  ESPN BRIDGE — 232 board players without an ESPN id matched to the Aug 31 pull by normalized name
     (65 T4, 53 T1, 47 T2, 40 T5, 27 T3). Each got eid, 2026 FP (ef), pace = FP x F, fp25, gp/gps/ab/ip and the
     current IL designation (38 ir changes). 108 of them were MLB producers frozen since the June FA imports —
     and their stored "2026 pace" turned out to be 2025 totals x 1.239 (Pepiot 1483 = 1197 x 1.239, Priester,
     Berríos, Westburg, P. López, Megill, R. Olson ...). ESPN shows 0 FP and IL-60 for most of them, so their
     June multipliers reset through the §13 short-circuits: Pepiot 1187 -> 950, Priester 1197 -> 943,
     JP Sears 817 -> 390 (pm 1.047 -> 0.50 on a real 157-FP season), Romy González 665 -> 278, Teel 782 -> 555.
     12 producers have no record in the pull (Musgrove, Thorpe, Bloss, Luciano, River Ryan, Wiggins, B. Mitchell,
     Clifford, Wenninger, Reimer, Z. Maxwell, J. Ferrer): their values stay June's; the one still carrying a June
     multiplier (Musgrove, 0.785) was retired to 1.00 pending a bridge, the rest already sat at 1.00.
     Yunior Marte is ambiguous in ESPN (two ids) and was left unbridged.
  2  FA HYGIENE — 25 free-agent records still carried their old roster name / level; cleared. The Inspector also
     no longer prefers rn over the FA test.
  3  PHASE PROMOTION (§10/§19.4, promote-only on fp25 + 2026 FP) — 16 T3s:
     Book->Established: Troy Melton (KCG), Juan Morillo (KSS), Yoendrys Gómez (DS), Jack Perkins, Andrew Alvarez,
     Jorbit Vivas, Juan Mejía, Nathan Church.  Honeymoon->Book: Max Clark (C-Town), Jordan Lawlar, Drew Romo,
     Adael Amador, José Fermín, Víctor Mesa Jr., Tyler Locklear, Zach Agnos.
     Tool-basis promotions move the maturation stage (0.60 -> 0.80 -> 1.00) and the phase factor (0.80 -> 1.15 -> 1.00).
  4  §11 PROXIMITY — the AAA/MLB bucket (-0.10 hitter / -0.05 pitcher) applied to the 179 MLB-stage tool-basis
     T3s the engine had carried at 0 (+9,916 RA; Evan Carter 0.864 -> 0.96, Max Clark 0.732 -> 0.828 with his
     Book step). eng.prox on the four Aug 31 records (Mautz, Thornton, Castellano, Anderson) reconciled to the
     Hit% they already carried. Eight off-formula tool Hit% values rebuilt from §10: Backhus 0.92 -> 0.317
     (his 0.62 bust had never been applied), Ewing 0.816 -> 0.96, J. Fernández 0.276 -> 0.461, S. Miles 0.40 -> 0.517,
     J. Arnold 0.649 -> 0.599 and T. Sykora 0.79 -> 0.74 (IL60 -0.05 was in their notes, not their Hit%),
     T. McKenzie, K. Drake.
  5  §19.6 RATCHET — every eng.rch record re-anchored to banked 2026 to-date (121 records, +18,507 RA). The peak
     had been frozen at a June to-date while the Aug 27/31 audits retired the pace multiplier against it:
        Cade Cavalli (KCG)      pk 477 -> 1337   RA  448 -> 1257  +$1.63
        Cam Schlittler (HC)     pk 971 -> 1668   RA 1004 -> 1725  +$1.45
        Nolan McLean (RC)       pk 699 -> 1292   RA  755 -> 1396  +$1.29
        Jacob Misiorowski (RC)  pk 1179 -> 1881  RA 1007 -> 1607  +$1.21
        Foster Griffin (KSS)    pk 528 -> 1156   RA  480 -> 1052  +$1.15
        Chase Burns (RC)        pk 863 -> 1349   RA  922 -> 1441  +$1.04
     13 non-ratcheted surpassers met both §19.6 conditions and fired (pm -> 1.00): Alec Burleson (banked 1366 >
     peak 942, was pinned at the 1.50 cap), Bryan Baker, Willson Contreras, Chase Meidroth, Miguel Vargas,
     Pete Crow-Armstrong, Royce Lewis, Jack Perkins, Kody Clemens, Nick Fortes, Andre Pallante, Huascar Brazobán,
     Anthony Seigler.
  6  §20.15 IMPORT PACE — pm now tracks 2 - 1/F = 1.153 (was locked at the June 1.50): Okamoto 623 -> 893 RA,
     Murakami, Imai (Pure 450 clears the 300 short-circuit). Santa, Ward, Pallette, Wenninger, Prieto stay at
     1.00 through the short-circuits, which take precedence.
  7  §13 GATE PASS over every player: 56 changes, all on bridged free agents; 0 leaks. 53 eligible players remain
     parked at 1.00 (ALLOW_NEW_PM off — the standing ruling, now written into §13).
  8  REPRICE — r = pc x pm x h; tjp rescaled by the exact Pure/pm ratio; tj = tjp x Hit%(age+k); RAW re-float; $.
  Also: GNDAILY.raw set to RAW (the EKG no longer reads it); Ian Seymour's unprocessed Aug 22 option "pending" cleared.

  ORG IMPACT ($ at each build's RAW)             v50.19      v50.20     delta   largest movers
    River Cats                                   98.62      107.32    +8.69   McLean +641, Misiorowski +600, Burns +519
    Kansas Sunflower Seeds                       81.39       86.39    +5.01   F. Griffin +572, Keaschall +501, Bowlan +382
    KC Gray Hotdogs                              89.47       94.41    +4.94   Cavalli +809, Melton +318, Sabrowski +171
    High Cheddar                                 78.81       83.60    +4.79   Schlittler +721, Headrick +363, Hancock +312
    C-Town Liquors (commissioner)                73.94       77.95    +4.01   Max Clark +289, Beeter +255, McGonigle +154
    Balking Dead                                 74.06       76.81    +2.75   G. Taylor +422, Okamoto +270, Benge +125
    Dirty Spikes                                 85.16       87.09    +1.93   Y. Gómez +214, Max Meyer +151, Messick +104
    MidwestBears                                 80.57       81.99    +1.42   Petersen +312, Lombard Jr. +62, Burleson +22
    Free-agent pool                             791.57      837.33   +45.76

  SURFACED, NOT CHANGED (need a ruling)
    - 55 bridged T4 prospects now show 2026 MLB time in ESPN (Luis Lara 236 FP / 36 G, Tommy White 167/24,
      Abimelec Ortiz 160/20, Schweitzer 149/14, Klassen 143/6, Bateman 131/17 ...). §4 says T4 = no MLB time but sets
      no cameo threshold; they stay T4 and the Inspector spine flags each ("2026 MLB production on file").
    - 21 T3s at/after peak age (Will Warren, Luis García Jr., Peraza, Hancock ...) — graduation deferred (no birthdates).
    - 12 of 31 production-basis Book T3s carry no maturation discount while the other 19 carry 0.80.
    - Roman Anthony's Hit% carries a legacy "permanent IL stack -0.02" from June that is not a current designation.

================================================================================
CALCULATOR CODE (patch_code_v50_20.py; identical in index.html and mobile.html)
  - Add-player click: the search boxes no longer listen for 'change' (blur re-rendered the list mid-click; every
    add took two clicks / taps). Filter selects keep it.
  - A player can be received by one side only; "Pick players" only when nothing is picked.
  - Saved trade sides persist {name, eid} and are re-resolved against the live board on load — no more last-week
    values after a refresh; unknown names dropped, duplicates collapsed.
  - Rule 5 panel tests the roster LEVEL (l === 'MLB'), not the ESPN roster name; reads the recapture record
    (Palencia: recaptured / exempt). Headrick, Harrison, Dingler, Tucker now read ON MLB ROSTER.
  - Manager EKG $ line divides by RAW_PER_DOLLAR (was GNDAILY.raw = 637.32, ~21% low). Career arc's retired
    steeper vet curve replaced by the §12 curve.
  - Inspector: Hit% chain shows level proximity and computes effective bust from (bust + proximity) x phase;
    phase label honest for T4; vets' x1.15 scarcity itemised; pace rows use Pure ÷ growth for pre-peak production
    players and the §13 month absorption (GN_ABSORB from GN_DATA_THROUGH); pm = 1.00 reasons cover tool basis,
    Honeymoon/Book, recency floor, parked-at-1.00.
  - Decision spine: step 3 reads 2025 FP from fp25; step 4 flags a ratcheted record whose banked total passed its
    stored peak; step 5 keys the gate off tier/phase (§13) and recognises recency-floor / ratchet retirements and
    the parked rule — no more false "stale" flags on Trout, Manaea, Sheehan and 100+ others.
  - Fade ladder: MLB stages inherit the AAA proximity bucket and proximity credit is never withdrawn on a step.
  - Tier labels T1-T5 (were TT1-TT5); free agents show "Free agent (was X)" not a stale roster; header v50.20;
    footer date; "90-day" comments; Options note; Chart.js poll stops after 10 s offline with a message;
    service worker pre-caches mobile.html; dead snapshot-chart code removed (HISTORY literal kept, 1.97 MB —
    drop it on ruling); ROS mode readouts say the sliders are inert.
  Verified in headless Chromium: first click adds, both-sides guard, stale-save re-resolve, Rule 5 statuses,
  EKG last-day $ = sum of p.d for shaped players, Inspector chains reconcile (Cunningham 0.96 x 0.490 = 0.470;
  Sheehan 760 ÷ 686 -> 1.086; Moreno scarcity line), no page errors; getValue/fade math finite for all
  2,118 players x every mode; fade-on never below fade-off.

================================================================================
PIPELINE
  update_calc_weekly_TEMPLATE_v50.20.py replaces update_calc_TEMPLATE_fixed.py (which wrote the ESPN team id into
  the TIER field on every roster move — the defect the Aug 25 audit repaired — and derived absorption from a
  hard-coded date). The new template writes tid only, derives ABSORB from DATA_THROUGH, bridges ids, and runs phase
  promotion, the ratchet re-anchor, import pace and the gate every week; invariants assert before any write.
  Dry-run against this build with the Aug 31 pull reproduces it with zero value changes.
  season_roll_lambda_v50.20.py: --apply --confirm-season-complete now writes the rolled PLAYERS literal and RAW
  into index.html and mobile.html (default beside the build, or --out DIR); refuses on any invariant violation.
  Dry run on this board at λ 0.40: 513 in scope, 384 down, 129 up, 152 clipped, 53 capped at peak, -8.8%.

STILL NOT COVERED (unchanged from v50.18/19): GNDAILY ends at SP152 (Aug 23) and GNROS still describes Week 20;
the 737 non-ESPN prospects carry forward unverified (MLB statsapi deferred by direction).

WORKBOOK: Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx was not touched by this pass; it still carries the v50.19
values for the 393 repriced players and re-syncs on the next weekly build (runbook step 5).

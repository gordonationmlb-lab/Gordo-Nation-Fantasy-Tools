GORDO NATION TRADE CALCULATOR — v51.14  ROSTERS MOVE AHEAD OF THE DATA, AND SAY SO (2026-09-22)
  ROSTER-ONLY refresh of v51.13. No valuation changed — not one of pc, r, t, tj, tjp, pace, eng,
  inj or im. The pull and data window are still those of v51.0-v51.13: scoringPeriod 173,
  matchup period 22, Week 22 data. No weekly refresh ran.
  Service worker: gordo-calc-v87-2026-09-13-v51.14.  GN_BUILD v51.14, GN_DATA_THROUGH 2026-09-13.
  NEW: GN_ROSTERS_THROUGH 2026-09-22 (scoringPeriod 182).
  RAW_PER_DOLLAR unchanged at 536.61.
  Acceptance: verify_calc_v51_14.py FAIL 0 (WARN 2 — the standing designation-lag warning, and
  the 9 T3s on a veteran basis from the Aug 25 audit).

================================================================================
1. WHAT CHANGED, IN ONE SENTENCE

  The board now says where every player actually is as of 22 September, while every number
  attached to him is still the number v51.13 computed from data through 13 September — and the
  build carries two separate stamps so the two windows can never be read as one.

================================================================================
2. WHY TWO STAMPS

  GN_DATA_THROUGH is the valuation window. GN_ROSTERS_THROUGH is the membership window. Until
  v51.14 they were the same date and one constant served for both. A roster refresh without a
  weekly refresh separates them, and a single stamp would then be a lie in one direction or the
  other. The visible build line in index.html and mobile.html carries both:

      v51.14 · data through Sep 13, 2026 · rosters through Sep 22, 2026.

  Any org total, positional rank or keeper view in this build is therefore NEW ROSTERS priced on
  13 SEPTEMBER VALUES. That is sound for "who owns whom" and for cap and construction questions.
  It is NOT a refreshed valuation of anybody, and must not be quoted as one.

================================================================================
3. THE ROSTER CHANGE (source: 2026/Data/GN_Rosters_2026-09-22.json, scoringPeriod 182)

  Pulled from the ESPN fantasy API against the authenticated session, byte-verified on transfer
  (SHA-256 2c1d56ba…a38c0, 107,583 bytes). Owner/SWID identifiers were stripped at the source.

  405 rostered players, 16 teams, 8 orgs — every per-org count reconciles against ESPN:
      Balking Dead 51 · C-Town Liquors 52 · Dirty Spikes 50 · High Cheddar 50
      KC Gray Hotdogs 49 · Kansas Sunflower Seeds 52 · MidwestBears 49 · River Cats 52

  21 board records changed org: 8 adds, 9 drops, 4 cross-org moves.
    adds   Eli Willits, Ethan Salas, Brady House, Rainiel Rodriguez, Theo Gillen (C-Town);
           Daniel Lynch IV, Zyhir Hope, Mason Montgomery (River Cats)
    drops  Josh Jung, Jacob Young (C-Town); Jeremiah Estrada, Jonathan Aranda, Emilio Pagan,
           Edwin Diaz (KC Gray); Pedro Ramírez, Hunter Gaddis, Trevor Rogers (River Cats)
    moves  AJ Blubaugh, Parker Messick (Dirty Spikes -> KC Gray); Payton Tolle (KC Gray ->
           River Cats); Luis Garcia Jr. (C-Town -> MidwestBears)

  NONE OF THESE WAS A TRADE. The full-season transaction log carries no messageTypeId 244 for any
  of them: all 8 non-lineup events are ADD/DROP through the free-agent pool, on 21 and 22 Sep.
  The ledger and Trade Court are unaffected.

  4 eids attached. Willits, Rainiel Rodriguez, Gillen and Hope were priced T4 prospects carried
  as FA with eid null, because an unrostered prospect never gets an ESPN id bridged. They are
  bridged now: 1,437 players carry an eid, up from 1,433.

  `il` (ESPN injury designation) was deliberately NOT updated. v50inj, inj and im are derived
  from it and recomputing them would be a model change, not a roster change.

================================================================================
3.1 THE WORKBOOK

  Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx was re-synced from this build by
  resync_ceiling_workbook_v51.14.py. 1_Player_Inputs refreshed 1,412 rows, 70 cells changed,
  Risk-Adj moved on 0 of them -- the change is membership, not value.
  2_Org_Rankings recomputed (River Cats 54,186 still first, KC Gray Hotdogs 50,811 second).

================================================================================
4. MEMBERSHIP SERIES

  GNDAILY.member is the history: eid -> runs of "<char><scoringPeriod>", char the team id in
  base 36, '.' free agent. Moving the board to SP182 without extending the series left the two
  disagreeing about 15 players. One group per moved player was appended at SP182 — the period
  the pull observed, not necessarily the period the transaction cleared. 617 series, up from 611
  (6 created for players who had none).

  verify_calc.py compared the board against membership AT THE PULL DAY, which a roster-ahead
  build can never satisfy. verify_calc_v51_14.py compares at GN_ROSTERS_THROUGH instead and
  prints both windows on the line. That is the only change to the acceptance script.

================================================================================
5. WHAT WAS NOT DONE

  - build.json still carries the v51.13 expectations. It was not advanced because this workspace
    is shared and v51.13 was built in it earlier today by another pass. Advance it when v51.14
    is adopted as current.
  - No weekly refresh. Week 23 and 24 stats, splits and box scores are not in this build.

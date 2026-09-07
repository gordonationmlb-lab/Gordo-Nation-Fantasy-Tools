GORDO NATION TRADE CALCULATOR — v50.21  WEEK 22 DATA BUILD (2026-09-07)
  First build past the postseason line. Data window moves to Week 22: scoringPeriod 166, matchup
  period 21 — PLAYOFF ROUND 1 — complete (SP153-166, Aug 24 - Sep 6). F = 162/143 = 1.1329;
  September absorption 0.90. No framework change; Methodology v11 still stands.
  Service worker: gordo-calc-v70-2026-09-07.  GN_BUILD v50.21, GN_DATA_THROUGH 2026-09-06.

  Run with update_calc_weekly_v50.21.py (the v50.20 weekly template, one substantive change —
  see BRIDGE below), then update_options_v50.21.py, stamp_v50.21.py and
  resync_ceiling_workbook_v50.21.py. Acceptance: verify_calc_v50.21.py, FAIL 0.

================================================================================
THE BRIDGE DECISION — why RAW barely moved
  RAW_PER_DOLLAR 497.64 -> 497.17 (-0.09%). Anchor pool 1,376 -> 1,391 eid-bearing r>0.

  This needed a ruling. The Week 22 pull returned ESPN's ENTIRE player universe — 3,935 records,
  where every prior pull effectively carried ~1.4k. Run unchanged, the id bridge matched 468 extra
  unrostered deep prospects and swept them into the anchor pool:

      EXISTING anchor pool      n=1,376   mean r = 497.6
      NEWLY BRIDGED (r>0)       n=  468   mean r = 131.6
      COMBINED                  n=1,844   mean r = 404.7   => every dollar +23.0%

  RAW is the mean raw value of the eid-bearing priced pool, so widening the pool with cheap
  prospects deflates the unit and inflates every dynasty dollar on the board. A +23% board-wide
  move in the week the World Series is being previewed, caused by ESPN changing what its endpoint
  returns rather than by anything that happened on a field, is not a valuation — it is an artefact.

  RULING (commissioner, 7 Sep 2026): the bridge indexes only the ACTIVE universe — 2026 fantasy
  points, a fantasy roster spot, or last-30 activity. That is the same 1,452-player subset shipped
  as GN_Universe_Active_Stats_2026.json, and the same universe prior pulls contained. 17 players
  bridged this week instead of 485; nothing genuinely active or rostered was excluded, and what was
  excluded had no 2026 production to sync anyway. Issue 22's dollars stay comparable with Issue 21's.
  689 board players still carry no ESPN id, unchanged in kind from prior weeks.

================================================================================
ENGINE DATA (update_calc_weekly_v50.21.py, report in refresh_report_2026-09-06.json)
  Board RA 762,833 -> 767,057 (+4,224): 290 up, 225 down. Invariants: ALL CLEAR.
  515 records repriced, 792 fantasy-point updates, 327 pace-multiplier changes.

  1  ROSTER SYNC — 4 org/level moves, 2 drops to free agency, 0 unbridged rostered players.
  2  INJURY SYNC — 94 designation changes; 272 pull records carrying a designation (273 board
     records read non-ACTIVE, the extra one a player ESPN no longer returns). 23 went onto one,
     53 cleared to ACTIVE (Ketel Marte, Will Smith and Blake Treinen off IL-60, Riley Greene,
     Josh Smith, JoJo Romero, George Lombard Jr.).
  3  PHASE PROMOTION (§10/§19.4, promote-only) — 7: A.J. Ewing, Owen Caissie, Cole Carrigg and
     Max Muncy (Ath) Book->Established; Craig Yoho, Joshua Báez and Jonah Cox Honeymoon->Book.
  4  §19.6 RATCHET — 111 eng.rch records re-anchored to banked 2026 to-date; 24 non-ratcheted
     surpassers met both conditions and fired to pm 1.00 (Zach Neto, Ivan Herrera, CJ Abrams,
     Gavin Williams, Reid Detmers, Taj Bradley, Zack Gelof, Brice Turang, Caleb Durbin,
     Henry Davis, J.T. Ginn among them).
  5  §20.15 IMPORT PACE — pm tracks 2 - 1/F, now 1.117 (was 1.153): Okamoto, Imai, Murakami.
     Santa, Ward, Wenninger, Prieto, Pallette stay at 1.00 through the short-circuits.
  6  §13 GATE — every player, every week. 76 eligible players remain parked at 1.00
     (ALLOW_NEW_PM off, the standing ruling).
  7  GNDAILY extended 152 -> 166 days (Mar 25 - Sep 6), 573 shapes rebuilt, 7 new, 2 txn nodes.
     This closes the gap v50.18/19/20 all shipped with: GNDAILY used to end at SP152 (Aug 23),
     so the EKG was two weeks behind the board it sat next to. It now runs to the data date.
  8  GNROS — 380 forms updated; replacement-level rn 0.7473 -> 0.7465 across 100 rostered RPs.
     GNROS described Week 20 in the last three builds; it describes Week 22 now.
  9  HISTORY — a 2026-09-06 snapshot of all 2,118 players appended (14 snapshots on file).

  A NOTE ON DIRECTION, because it looks wrong and is not: several players who went ONTO the IL
  this week went UP in value. §13 short-circuits the pace multiplier to 1.00 on the IL — a player
  cannot be charged for a pace he is not permitted to post — so retiring a sub-1.00 multiplier
  outweighs the -0.02 hit% haircut. Shane McClanahan (IL-15) 727 -> 952 is the clearest case:
  1445 x 1.00 x 0.659 = 952. Luis Robert Jr. (IL-10) 435 -> 849 = 1023 x 1.00 x 0.83. Eric Lauer
  (IL-15) 572 -> 833 = 957 x 1.00 x 0.87. Every one reconciles on r = pc x pm x h to the point.
  The mirror case is Logan Webb, healthy and falling 1064 -> 938 = 1594 x 0.661 x 0.89, because a
  live pace below expectation is exactly what the multiplier is for.

  ORG IMPACT ($ at each build's RAW)          v50.20      v50.21     delta   largest movers
    Free-agent pool                           837.33      840.48    +3.14   Luis Robert Jr. +414, Eric Lauer +261, Travis d'Arnaud +250
    KC Gray Hotdogs                            94.41       96.72    +2.31   Cole Carrigg +133, Ivan Herrera +109, Pete Crow-Armstrong +94
    High Cheddar                                83.60       85.27    +1.67   Shane McClanahan +225, Walbert Urena +143, Garrett Cleavinger +122
    River Cats                                 107.32      108.86    +1.54   A.J. Ewing +226, Willi Castro -90, Konnor Griffin +72
    MidwestBears                                81.99       82.57    +0.59   Rafael Devers +103, Drew Rasmussen +62, Jeff McNeil +61
    Balking Dead                                76.81       77.30    +0.48   Steven Okert -81, Brooks Lee +62, Taylor Ward -60
    Kansas Sunflower Seeds                      86.39       86.75    +0.36   Logan Webb -126, TJ Rumfield +113, Gunnar Henderson -90
    Dirty Spikes                                87.09       87.11    +0.01   Corbin Carroll -72, Parker Messick +71, Kody Clemens +71
    C-Town Liquors (commissioner)                77.95       77.80    -0.16   Jackson Holliday -83, Peter Lambert +70, Colton Cowser -55

  The two World Series clubs move least: Dirty Spikes +0.01 and, on the other side of the bracket,
  KC Gray Hotdogs +2.31 on Carrigg's promotion and Herrera's ratchet. Nobody bought a title in the
  last two weeks — both finalists are being paid for what they already had.

================================================================================
OPTIONS TRACKER (update_options_v50.21.py)
  495 -> 502 players, 1,079 -> 1,115 events, 248 -> 250 burns, 34 still out of options.

  The weekly template does not touch OPTIONS_DATA — options are a function of the league ACTIVITY
  feed, not the player pool — so this ran separately. ESPN returns only a trailing window of that
  feed (500 records, Aug 19 - Sep 7), which cannot rebuild the season the way Week 20 did. It
  extends the stored ledger instead, and uses the five-day Aug 19-24 overlap to prove the parse
  before trusting anything past it. Three findings came out of that check, all of which would have
  shipped silently without it:

  1  THE FEED READS to<from, NOT from<to. Each token is "6<2:pid": the arrow points at the
     RECEIVING club. Read the other way round, every MLB->AAA demotion inverts — and a demotion is
     precisely what burns an option under VI(b)(3). The first run produced Juan Soto with two burns
     and OUT OF OPTIONS on a fabricated Aug 31 demotion. The overlap check caught it as 36 events
     whose burn flag was the exact negation of the stored record. He has one burn and one option left.
  2  THE STORED HISTORY STOPS MID-DAY ON AUG 24. The Week 20 build ran during the deadline, so it
     holds that day's moves only up to its own pull time; four adds later the same day (A.J. Ewing,
     Landen Roupp, Noah Cameron, Tyler Mahle) were missing. A single league-wide date cutoff drops
     them. The extension therefore reclassifies from Aug 24 inclusive and keeps, per player, only
     what is strictly newer than that player's own newest stored event.
  3  MATCHING ON THE DETAIL STRING DOUBLE-WRITES A RULED EVENT. Daniel Palencia's Aug 24 add is
     stored as "Reacquired by Clam Shack Knucklers (AAA) — RULE 5 RECAPTURE, no option charged
     [Art. V(b)(4)(C)(i)]", wording that came from the commissioner's ruling and that no
     re-derivation reproduces. The per-player watermark suppresses it correctly; a detail-string
     match appended a duplicate. His record stands untouched: 2 burns (Apr 20, Jun 19), 0 remaining,
     the recapture not charged.

  NEW BURNS — two, both processed MLB->AAA trades, both cross-checked against the live rosters:
     JJ Wetherholt      Aug 31   River Cats (MLB) -> Flying Squirrels (AAA)      1 burn, 1 remaining
     Willson Contreras  Sep 1    High Cheddar (MLB) -> hicheddar AAA (AAA)       1 burn, 1 remaining
  NEW TO THE LEDGER — DL Hall, Drew Sommers, Hayden Wesneski, Mickey Gasper, Pedro Ramirez,
     Tim Tawa, Tyler Mahle.
  Nobody is over the 2-option limit; remaining == 2 - burns for all 502; every event carries a date.
  Ian Seymour's Aug 22 trade is still unprocessed and still labelled as such.

================================================================================
THE OTHER THREE TOOLS
  INJURY TRACKER    all 409 rostered players cross-checked against the pull: 0 ir mismatches.
                    59 of those 409 carry a designation; 273 across the whole 2,118-record board.
  EKG ORG VALUE     GNDAILY 166 dates == its own days field, all 581 series exactly 166 long,
                    GNDAILY.raw == RAW_PER_DOLLAR (the v50.20 fix holds), 8 orgs each with a txn
                    node set, 16 fantasy teams, 607 membership series.
  PLAYER INSPECTOR  every field the inspector reads is present on all 2,118 records; d == r/RAW
                    for all; pace == round(ef x F) for every player still in ESPN's pool.
                    Three players — Austin Warren, Zach Dezenzo, Jack Anderson — are FROZEN: ESPN
                    has dropped them from its universe, so ef and pace both hold at the last week
                    it carried them (their ratio is ~1.29, i.e. week 18's F). That is deliberate.
                    A player ESPN has stopped tracking is not accumulating production either, so
                    re-scaling a frozen ef by an ever-growing 162/games factor would manufacture a
                    projection for someone who has stopped playing. They read identically in v50.20.

================================================================================
CHROME (stamp_v50.21.py)
  Three hand-written prose stamps are not touched by the template and were still reading v50.20:
  the Trade Desk footer ("as of August 30, 2026 (Week 21 data...)"), the mode line ("v50.20 · data
  through Aug 30, 2026") and the options ledger note. All three now read the Week 22 window. Each
  substitution is asserted to match exactly once — "Week 21" and "v50.20" also occur hundreds of
  times inside PLAYERS[].notes, which is the per-player audit trail of when each value moved, and
  rewriting that would falsify the record.

================================================================================
WORKBOOK (resync_ceiling_workbook_v50.21.py)
  Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx re-synced — the v50.20 note said it would
  re-sync on the next weekly build, and this is it. 1,412 rows refreshed, 8,077 cells changed,
  780 Risk-Adj values moved, 0 rows without a calculator record.

  All 24 calculator-derived columns are now refreshed in one pass. Three earlier scripts each owned
  a slice (update_player_inputs.py: 11 columns; update_workbook_tiers.py: 5; update_options_workbook.py:
  1) and everything else drifted. The consolidation was gated on a check that the four columns
  nothing had ever written — Pos, Age, Healthy Base, Conf — already agreed with the calculator; they
  did, exactly, so nothing curated was overwritten. Phase was the one real drift: 23 rows, every one
  a forward promotion, no reversals, which is what a promote-only engine must produce. The script
  refuses to write if any phase change runs backward.

  Column 19 "Options Remaining" now carries the live ledger instead of the blanks it held.
  2_Org_Rankings recomputed (River Cats 54,120 still first, KC Gray Hotdogs 48,085 second).
  Sheets 3-12 re-stamped [NOT REFRESHED WK22] — they are unchanged and now say so honestly.

  IT IS NOT WRITTEN AT THE LEAGUE ROOT, ON PURPOSE. The root
  Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx is a HARD LINK to
  2026/GN_v50.19_wk21_2026-08-31/Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx — one inode,
  two names — and writes on this share land in the existing inode rather than replacing the
  directory entry (verified: mv over an existing file changed both names). Saving over the root
  path would therefore have silently rewritten the archived v50.19 snapshot and destroyed the
  ability to reproduce that build. v50.21 ships as
      2026/GN_v50.21_wk22_2026-09-07/Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED.xlsx
      Gordo_Nation_Dynasty_CEILING_Workbook_UNIFIED_v50.21.xlsx   (league root)
  and the root UNIFIED file still holds v50.19 values. Swapping it in is a decision to make
  deliberately, not a side effect of a refresh; the two archives are confirmed intact
  (v50.19: 529 KB, "Updated: August 31, 2026").

================================================================================
STILL NOT COVERED
  - The 737 non-ESPN prospects carry forward unverified. MLB statsapi is the right source for
    proximity / T4->T3 and remains deferred by direction.
  - 55 bridged T4 prospects with 2026 MLB cameos are still T4; §4 sets no cameo threshold.
  - 21 T3s at or past peak age await graduation (no birthdates on file).
  - Roman Anthony's Hit% still carries the June "permanent IL stack -0.02" that is not a current
    designation.
  - HISTORY has a duplicate 2026-08-10 snapshot date, inherited from Week 19. Harmless, uncorrected.
  - season_roll_lambda_v50.21.py is staged but NOT run. It is a season-roll tool and the season
    is not over; it needs --apply --confirm-season-complete after the World Series.

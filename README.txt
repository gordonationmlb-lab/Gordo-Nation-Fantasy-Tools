GORDO NATION TRADE CALCULATOR — v51.19  PLAYER COMPARE; STATCAST FROM YOUR BROWSER, NEVER PRICED; ANONYMOUS COUNTS (2026-09-26)
  Built on v51.18. Same pull and data window: scoringPeriod 173, matchup period 22, Week 22 data.
  Rosters through 2026-09-22 (scoringPeriod 182). No weekly refresh ran. No price, panel or rank moved.
  Service worker: gordo-calc-v92-2026-09-13-v51.19.  GN_BUILD v51.19, GN_DATA_THROUGH 2026-09-13,
  GN_ROSTERS_THROUGH 2026-09-22, GN_INJ_OPENING 2027-03-25.
  RAW_PER_DOLLAR unchanged at 537.96.
  Acceptance: verify_calc.py FAIL 0 (WARN 2, both standing); see section 7.
  Written into calc/ and build.json by build_v51_19.py like v51.18; package.py made GordoNation_Calculator_v51.19/
  and its zip. The deploy grows from 19 files to 21 (gn-track.js, gn-compare.js); nothing Statcast is in it.
  Methodology v19 (Reference/Trade_Calculator_Methodology_v19.docx) records it.

================================================================================
1. WHY

  On 26 Sep 2026 the commissioner asked for a way to put up to five players side by side with the Player
  Inspector's full formulas, and with Statcast beside them.
  - The formulas are the Inspector's own. Compare re-derives nothing: every priced figure in it is the number the
    Inspector prints for that player, and the value row is the Trade Desk's.
  - Statcast is shown, never priced. v51.18 tested it three ways against bars written down before any test ran
    (statcast/PREREGISTRATION.md): a luck-adjusted rate for the pace and carry instruments, a box-score term in
    Production Value, and a rookie stick model. All three FAILED; build.json 'statcast' records the verdicts. The
    engine's points-based terms already carry what Statcast added, so in Compare it is context for a manager's
    own judgment, labelled "context only · not part of the price", and nothing in it reaches r, pc, h, pm, im,
    tj, tjp, d or RAW.
  - The same day the commissioner ruled on where the Statcast numbers come from (option (b), section 3) and asked
    for anonymous counts (section 4): the aim is to learn whether anyone besides the commissioner uses the site
    before more is built.

================================================================================
2. THE COMPARE VIEW                                        gn-compare.js (source: compare/gn-compare.js)

  A new section on both pages, below the Trade Desk: up to five players side by side.
  WHAT IT SHOWS
  - Value (your settings): the Trade Desk's own getValue / fmtValue, so the cell reads what the side lists read.
  - Headline RA and $, then the chain in the Inspector's order: Pure ceiling, x Pace, = pace-adjusted peak, x Hit%,
    = healthy RA, x Injury, = headline RA, with the Inspector's identity check. Each group opens to the Inspector's
    own rows ("Expand all formulas" opens them all).
  - The decision sequence (tier, phase, basis, ratchet, pace gate), the ten-season trajectory on one scale for all
    columns with the cells the value row uses shaded, the Inspector's notes on request, and the Statcast block.
  - "Differences vs the first column" and the "best in row" mark grade the DISPLAYED numbers with the five-cent floor,
    as the Trade Desk's verdict does. There are no totals: summing sides is the Trade Desk's job.
  - The 33 T2 recency-floor chains that do not reconcile on the Inspector today (v51.18 section 8) say so where
    Compare shows the row.
  - How it reads the Inspector: renderInspector was split. gnInspectorHTML(p) returns the panel as a string and
    renderInspector writes it (keeping its empty state and INSP_CURRENT). Every panel is byte-identical to v51.18 on
    all 2,118 records under bust risk off / on x list / tree (section 7).
  ENTRY POINTS
  - Compare's own search; "+ Compare" in the Player Inspector's header (it reads "Compare full (5/5)" when there is no
    room); "Compare picks" beside the Trade Desk's Clear and "+ Trade Desk picks" inside Compare; "+ Inspector's
    player"; and "Inspect" on any column, which opens that player in the Inspector.
  - While the section is off screen a tray at the bottom holds the comparison, with View to jump back (one row on a
    phone, View always on screen).
  - A player just added is brought into view when the table scrolls sideways (1023 px and narrower, every phone).
  SETTINGS FOLLOW THE TRADE DESK
  - Compare's controls are the Trade Desk's own: value mode (Risk-Adj / $ / ROS), Career years, Cumulative /
    Single, the RA / Pure blend and bust risk. A change in either place changes both. ROS greys out the years, the
    blend, the year mode and bust risk in both places, as the Trade Desk always has.
  - Career years runs 1 to 10; at an end the step is dimmed and announces the limit instead of doing nothing.
  LINKS
  - The comparison is kept in this browser and in the page address (#compare=...: ESPN ids, else MLBAM ids, else a
    folded name). "Copy link" copies the address; the button itself reads "Link copied ✓", or "Copy the address
    bar" when the browser refuses the clipboard, then goes back.
  - A link never overwrites the comparison a browser had saved: the linked players show, and "Restore my comparison"
    brings the saved set back. "Clear comparison" can be undone.
  - A link to players this browser was not already showing opens the page AT Compare (it is 2,000+ px down on a
    desktop, further on a phone). A reload or Back keeps the browser's own position, and a viewer's own saved set
    in the address (the desktop / phone switch, a bookmark) does not move the page.
  - A link is read up to 30 entries, five players at most. Unknown or malformed entries, and a saved player no longer
    on the board, are named in a line under the header rather than dropped silently.

================================================================================
3. STATCAST IN THE BROWSER: FETCHED BY EACH VIEWER, NEVER PRICED, NOTHING BUNDLED

  THE RULING (the commissioner, 26 Sep 2026, option (b)): each manager's browser fetches Baseball Savant's CSV
  exports at runtime when Compare needs them. NOTHING Statcast is bundled in the deploy or committed to the repo:
  no Statcast data file, no CSV. Savant's CSV endpoints send access-control-allow-origin: * (checked 26 Sep), so the
  page's CSP gains connect-src https://baseballsavant.mlb.com. Not taken: (a) links only, (c) a bundled data file,
  (d) asking MLBAM.
  WHAT IS FETCHED, AND WHEN
  - Only while Compare is on or near the screen with a player in it. A comparison saved below the fold costs no
    request at load; scrolling to it (or opening a link, which lands there) starts the fetch.
  - First use: five 2026 leaderboards (percentile rankings and custom, batter and pitcher; batter max EV), 0.41 MB.
  - Anyone showing a 2026 pitching line: two grouped pitch searches (fastball extension, CSW), 0.80 MB.
  - A player whose 2026 MLB sample in a role is under 100 PA / BF: that role's 2025 leaderboards (0.42 MB for both
    roles) and the Triple-A / Florida State League search exports, which every prospect also gets (hitting 1.61 MB,
    pitching 2.17 MB). Those two are the only tracked minor leagues; a Double-A, High-A or rookie-ball player reads
    "No public tracking at this level".
  - 24 exports in all, 5.4 MB decoded (smaller on the wire when Savant compresses). MLB hitters alone cost 0.41 MB,
    1.21 MB once a pitcher is in; a hitter prospect 2.24 MB; a pitcher prospect 2.77 MB; a hitter prospect and a
    pitcher prospect beside MLB pitchers all 24, 5.4 MB (measured in the browser for Judge, Skubal, Mason Miller,
    Franklin Arias (Triple-A) and Anthony Eyanson (a Double-A pitcher, whose exports are read to say so)).
  - A player's lines depend on him alone, never on who else is compared, and each column waits only for its own
    exports. Requests go with credentials omitted and no referrer.
  CACHING
  - Each answer is kept in this browser's Cache Storage ('gn-savant-v1') for 12 hours, so a reload or the other page
    asks for nothing. A copy up to 7 days old is used only when Savant does not answer or answers with something
    unreadable, and the block says so.
  - Each request has a 15 s timeout (30 s for the search exports) and one retry; a failure is remembered for a minute.
  - The service worker never intercepts, caches or precaches a cross-origin request, and from v51.19 its activate
    step keeps gn-savant-* (a deploy is no reason to fetch the copies again). The loader retires older gn-savant-v*
    stores itself.
  FAILURE STATES (the rest of Compare is never held up)
  - "Statcast unavailable right now — Savant didn't answer." / "Savant's format changed, so these numbers can't be
    read right now." / "Savant has no rows for this yet." Each adds "Nothing above depends on it." and Try again,
    and every column keeps its Savant link.
  - An old copy in use: "(Savant couldn't be read just now, so this is the copy this browser saved then)".
  ON SCREEN
  - The band "Statcast · context only · not part of the price"; the note that nothing in the block changes Pure,
    pace, Hit%, injury, RA, $ or the trajectory; both dates ("Savant, fetched <time>" and "Prices through
    2026-09-13 (v51.19)").
  - Bars: right = better for the player. MLB bars rank against Savant's own groups. FB velo and FB spin, which Savant
    ranks on a different fastball measure, are ranked here over the same group and marked *. Triple-A and FSL bars
    rank within the level only and are not age-adjusted. "not ranked" means outside the group, never zero.
  ATTRIBUTION
  - Every block ends "Data: Baseball Savant / MLB (MLB Advanced Media, L.P.)", and each column links to the player's
    Baseball Savant page (a new tab, noopener noreferrer).

================================================================================
4. ANALYTICS: ANONYMOUS COUNTS                                   gn-track.js (source: compare/gn-track.js)

  GoatCounter, site 'gordonation' (counts go to https://gordonation.goatcounter.com/count; the dashboard is
  https://gordonation.goatcounter.com).
  WHAT IS COUNTED
  - Page views of index.html and mobile.html.
  - Five named events, each at most once per page view and only after the viewer has done something (a trade or ROS
    mode restored at load is not an event):
      inspector-open        the Player Inspector shows a player
      trade-evaluated       a Trade Desk add or remove that leaves both sides filled (a mode or slider change over a
                            restored trade is not one)
      compare-used          a player is added to Player Compare
      compare-link-copied   Compare's Copy link succeeded
      ros-mode              the ROS value mode is chosen
    An event carries its name as its page and title, and nothing of the page it came from.
  WHAT IS NOT
  - No cookie. No name, team, player, trade, search text or comparison. The part of the address after # is never
    sent, so a #compare= link's players stay in the browser.
  - What GoatCounter itself records with a view is the page, the referring site, browser, screen size and country;
    by GoatCounter's own account it keeps no IP address.
  - Nothing is counted from localhost or a private address (allow_local stays off) or inside a frame.
  HOW IT LOADS
  - count.v5.js from gc.zgo.at, version-pinned with its Subresource Integrity hash
    (sha384-atnOLvQb9t+jTSipvd75X2yginT4PjVbqDdlJAmxMm+wYElFmeR6EmLP5bYeoRVQ, GoatCounter's published v5 value, equal
    to the hash of the fetched file). A browser refuses the file if one byte differs. CSP: script-src + gc.zgo.at;
    img-src and connect-src + gordonation.goatcounter.com. A blocked or offline counter changes nothing on the page;
    gnTrack never throws and reads or changes nothing a price is computed from.
  THE COMMISSIONER'S OWN DEVICES
  - Open the site once in each browser on each device with #toggle-goatcounter at the end of the address (e.g.
    .../index.html#toggle-goatcounter). GoatCounter confirms, and that browser is not counted from then on; the
    same address turns counting back on. Compare leaves that hash in place at load, even with a saved comparison.
  A ONE-LINE NOTE FOR THE LEAGUE (suggested)
    "The trade calculator now keeps an anonymous visit count (GoatCounter: no cookies, no names, nothing you search
    or compare is sent), just to see whether tools like the new Player Compare get used."

================================================================================
5. THE DEADLINE BADGE (#gnDlCount)                                             index.html, mobile.html (CSS)

  The trade-deadline banner's countdown badge was set not to wrap, which held both pages 15-55 px wider than a
  320-360 px screen: a sideways scroll on the most common Android width, with or without Compare. At 400 px and
  narrower it may now wrap (one rule in each page's banner style block:
  @media (max-width:400px){#gnDeadlineInner .gn-dl-count{white-space:normal;max-width:100%;text-align:center;}}).
  No markup or script changed. Measured after: no sideways scroll at 320, 375, 780, 1024 or 1280 px.

================================================================================
6. THE WORKBOOK

  No re-sync: nothing it carries moved. Every input resync_ceiling_workbook_v51.18.py reads a value from is
  byte-identical to v51.18 -- the PLAYERS, GNDAILY, OPTIONS_DATA and RULE5 literals, RAW_PER_DOLLAR, the data,
  rosters and injury-opening dates, and every build.json key it reads (data window, pull, injury module, gnfv,
  attrition, time discount, statcast). build.json moved only in identity (build, build_prev, raw_per_dollar_prev,
  sw_cache), the new 'compare' and 'analytics' blocks and pre_roll.order's closing pointer. All 1,412 rows of
  1_Player_Inputs match the v51.19 board on Risk-Adj and $Value, and 2_Org_Rankings stands (River Cats 54,334 first,
  KC Gray Hotdogs 50,802 second, Kansas Sunflower Seeds 48,073, High Cheddar 45,502, MidwestBears 44,989, Dirty
  Spikes 44,772, C-Town Liquors 42,947, Balking Dead 42,519). The workbook therefore still reads "calculator
  v51.18" and Methodology v18, and its 0_README's pointer to README_v51.18.txt now means notes/README_v51.18.txt.
  The next re-sync runs v51.18 -> that build.

================================================================================
7. GATES

  NOTHING PRICED MOVED                                     inspector_equiv_v51_19.js (run by build_v51_19.py)
  Packaged v51.18 against this calc/, each loaded as gn-app.js alone AND as the full page stack:
  - every Inspector panel byte-identical on all 2,118 records under bust risk off / on x list / tree (sha 06c0ee3d /
    88073922 / 3f9b37c8 / 4f7a6733 in both builds); gnInspectorHTML(p) equals the panel and touches nothing;
  - getValue and fmtValue identical over 103 settings (RA, $ and ROS; Career years 1-10; single / cumulative; blend
    0 / 35 / 100; bust risk on / off): 218,154 checks, 0 differences;
  - PLAYERS, GNDAILY, OPTIONS_DATA and RULE5 byte-identical; PLAYERS == PLAYERS_2026-09-26_v51.18.json; r, pc, h, pm,
    im, tj, tjp and d equal on every record; RAW_PER_DOLLAR and GNDAILY.raw 537.96;
  - Compare's value cells equal getValue and PLAYERS does not move while Compare renders;
  - the project's inspector_check_v51_18.js gives the same report on both builds (the 33 standing recency-floor
    rows). The gate fails on a one-character panel change and on a 1e-9 change in one value.
  gn-app.js differs from v51.18 only by the split (three anchors) and GN_BUILD; each page by insertions plus two
  changed lines (the CSP and the build line).

  build_v51_19.py   guard: calc/ is the packaged v51.18 (folder and zip agree), v51.18's identities exact, the
                    roll's age audit reproduces build.json. Sources: one IIFE each; gn-compare.js has one fetch(),
                    names no origin but Savant's and never calls GoatCounter itself; gn-track.js's allow-list is the
                    five events, prototype-free, and its one GoatCounter call sends only the event's name. Then the
                    page, CSP, GoatCounter-tag and service-worker checks and the gates above. --reapply reproduces
                    every calc/ file, build.json and the report byte for byte.
  verify_calc.py    FAIL 0, WARN 2 (the 23 designation-vs-module lags and the 9 T3s on a veteran basis, both
                    standing, as in v51.18). New in v51.19, both modes:
                    - gn-track.js and gn-compare.js load in order, and no page loads a script outside the list;
                    - the only remote scripts are the pinned Chart.js and count.v5.js, each under its SRI hash, and
                      exactly one async GoatCounter tag with no settings;
                    - the CSP is exactly v51.18's plus the four sources;
                    - calc/ holds the deploy set, gn-history.js and backups and nothing else, and nothing in it names
                      a Statcast data file;
                    - calc/gn-compare.js and gn-track.js equal their compare/ sources and the sha256s build.json
                      records, and the build's rules on them hold in what ships;
                    - the service worker precaches every page script, returns before any cross-origin request and
                      keeps gn-savant-*; build.json 'analytics' names the same hash as the pages.
                    Negative tests on a mirror of this folder: the v51.18 pages and worker fail 14 ways; a
                    gn-compare.js whose track() sends the comparison's keys to GoatCounter 3 (1 when calc/, compare/
                    and build.json are all changed to match); a sixth event 1; an event path carrying the address 3;
                    a Savant CSV under another name 1; a data script loaded by both pages 3; a second unpinned
                    count.js 2; Chart.js without its SRI 1; compare/ missing 2; a hidden CSV 1. The gate as first
                    built passed all ten probes with FAIL 0; five of them are the headless verifier's.
  package.py        APPFILES + gn-track.js, gn-compare.js; refuses a file in APPFILES or calc/ whose name says
                    statcast or savant, or any CSV; the app zip (the deploy) must carry none, and neither may the
                    build zip's calc/. The build zip is the reproduction archive of this whole folder and carries
                    statcast/data/ (the v51.18 test pulls, gitignored); packaging prints how many raw Savant CSVs
                    that is instead of calling it clean (section 8).
  stamp.py          dry run on v51.19: the page chrome and this card current.
  update_calc_weekly.py   read side: its preflight refuses (no newer pull), as it should. Write side: run end to end
                    with --apply on a scratch copy fed a one-day-newer pull; the .tc-sub, rosters and cache stamps
                    each matched once, gn-compare.js and gn-track.js were left alone, build.json kept both blocks.
  season_roll.py    --fixture rehearsal on a mirror: verify_calc --roll FAIL 0; the roll carries gn-track.js and
                    gn-compare.js, restamps the worker and the build line, keeps build.json 'compare' / 'analytics'.
  Compare's own checks (in the session's scratch folder, outside the repo and the deploy, because they read cached
  Savant CSVs): the in-browser loader against a Python reference on every board player, failure paths, links,
  loading, markup and a round-4 check (the link landing, the name keys), all run against this calc/. In a real
  browser (the desktop app's Chromium pane, phone widths emulated): the layout driver from 1280 to 320 px on both
  pages, re-run on this build at 1280, 780 and 375 (mobile.html); a real service-worker install of this worker (it
  precached all 20 entries, deleted the v51.18 store and kept gn-savant-v1); live Savant under the page's CSP (24 of
  24 exports answered); the link landing, Copy link, the Career-years ends and a new column brought into view, with
  real key presses.
  The build verifiers' findings of 26 Sep are fixed in this build: the four gate gaps above; Copy link's silent
  result; a new column left off screen; a link opening at the top of the page; the phone tray's 12 px strip beside
  View; the Career-years ends; a stray space in a name key; the full-compare button's tooltip; the first-use sizes
  above; the pre-roll pointer (below).

================================================================================
8. STILL OPEN

  Carried from v51.18 (README_v51.18.txt is in notes/):
  * Ruling D-b: nine T1s below peak age by birth date, held T1.
  * The §4 resolver's sole-MLB-line extension (Carlos Rodriguez; 7 ids, or 6 verbatim). No value moves.
  * The injury re-run after the age fix: Suarez 624 -> 589 and Steele (Balking Dead) 807 -> 851. As built it happens
    at the pre-roll injury re-run; apply it sooner only on the commissioner's word.
  * Graduation maturation: a production-Book T3 who graduates to T1 at the roll keeps his x0.80 inside Pure. At this
    roll 8 relievers (Winn, Klein, Bachman, Halvorsen, Morgan, Vargas, Contreras, Englert): rolled RA 1,650, about
    2,063 if released.
  * Duplicate MLBAM ids: 687209 (the Maxwells; Zachary Maxwell's age fix held) and the 678606 name claim.
  * How pace multipliers reopen in 2027 (the weekly script; the roll resets every pm to 1.00).
  * McKenzie / Garrett (T5 depth on an old career best, or a T1 clock), REPACE v20 in four Pures, and the 9 T3s on a
    veteran basis (4 graduate at the roll) -- from v51.13.
  * The scoring map: the pending IP1 / SV12 / HR6 / no-fielding map is the league's decision.
  * The Inspector at the roll: on a rolled board 442 Pure chains need a 'documented adjustment' row, because the
    roll's own Pure step is not in the chain. Close before v52.0 ships. (The 33 T2 recency-floor chains already fail
    to reconcile today; Compare shows them as the Inspector does.)
  * The roll's tier re-read cannot move a tool T3 with neither eng.aod nor eng.bd (Jonathan Harris, Zach Thornton);
    14 tool T3s reach peak age by 30 June 2027 but not by opening day and stay T3 a year, as the rule is written.
  * 45 records have no birth date from any source.
  * Statcast pricing: not re-proposed without new data (v51.18 section 1). Compare shows it; that is not a reopening.
  * The pre-roll run order below, which the roll enforces for the switch.
  New in v51.19:
  * MLB's terms of use, §1(xi), bar automated collection. That bears on the pipeline's own statsapi pulls (birth
    dates, debuts, MLB lines: pull_mlb_people_v51_13.py, the v51.18 MLBAM bridge) and now on each viewer's browser
    fetching Savant's CSVs, which is option (b) as ruled. Noted to the commissioner; not ruled on.
  * Real devices. Every browser test ran in the desktop app's Chromium pane with phone widths emulated. Not yet seen
    on an iPhone in Safari (sticky header cells inside the sideways-scrolling box, scroll snapping, the one-row tray,
    the link landing) or on an Android phone.
  * A live GoatCounter count from the deployed site (localhost is never counted) and the #toggle-goatcounter
    confirmation, both to check on the dashboard after the deploy.
  * When 2025 lines are fetched: only for a role whose 2026 MLB sample is under 100 PA / BF, so regulars show no
    year-over-year marks. Fetching the five 2025 leaderboards for everyone (0.42 MB) would. A one-line change either
    way; the commissioner's call.
  * First-use cost of a prospect: 2-3 MB, 5.4 MB for a hitter and a pitcher prospect together (section 3); kept 12
    hours per browser. The commissioner's call whether that is acceptable on phones.
  * Savant data outside the deploy: the build zip (package.py's reproduction archive, never the deploy) carries
    statcast/data/, the v51.18 test pulls, as it did in v51.18 -- whether it should is the commissioner's call; and
    two Statcast-derived CSVs have been tracked in the repo since the xFP Anchor Study (commit 7d7b8ef:
    gn_statcast_2019_2025.csv, gn_statcast_v2_2019_2026.csv) -- whether to untrack them likewise.
  * Compare reads the Inspector's markup (section headings, formula-row classes). A later Inspector wording change
    shows "Section not found" in a column rather than a wrong number, but the check that catches it lives in the
    session's scratch folder; the checks that need no Savant data (panel parsing, links, markup) should move into
    this folder before the next Inspector change.
  * verify_calc.py's r identity keeps its v51.17 tolerance of 1 outside --roll; a hand edit of r by 1 after a build
    passes it (build_v51_19.py's own gate catches it).

RUN ORDER TO REPRODUCE
  mv README_v51.18.txt notes/
  python3 build_v51_19.py --apply            # calc/ (backups *.pre-v51_19), build.json, report; copies this README
                                             # to calc/README.txt (--reapply: back to v51.18 from the backups, then apply)
  (no workbook re-sync: nothing it reads moved -- section 6)
  python3 ../../../Reference/patch_methodology_v19.py --apply     # Methodology v19 (no PDF)
  python3 verify_calc.py
  python3 package.py --apply

PRE-ROLL RUN ORDER (build.json pre_roll.order; season_roll.py refuses a real roll that skips the switch)
   1. The final weekly refresh (update_calc_weekly.py and its run order), on the final 2026 data.
   2. The injury module's post-season feed (injury_v2_data_<date>.json, named in build.json), then
        python3 apply_injury_v2.py --apply
   3. build.json regular_season_end, from the final 2026 schedule.
   4. python3 pre_roll_basis_switch.py . --out DIR --report DIR/switch_report.json     (DIR outside this folder)
   5. Promote:  cp DIR/gn-app.js calc/gn-app.js
   6. python3 apply_injury_v2.py --apply     (the switched records lose the tool carve-out; RAW moves)
   7. Restamp the README card: its RAW_PER_DOLLAR line must end at build.json raw_per_dollar
      (e.g. '538.06 -> 537.96 -> 539.43.'); then cp README_<build>.txt calc/README.txt
   8. python3 verify_calc.py                 (FAIL 0)
   9. python3 season_roll.py . --out ROLLDIR, then with --apply --confirm-season-complete   (ROLLDIR outside)
  10. python3 verify_calc.py --roll ROLLDIR  (FAIL 0)
  11. The commissioner's OK.
  12. Promote ROLLDIR to calc/ and package v52.0.

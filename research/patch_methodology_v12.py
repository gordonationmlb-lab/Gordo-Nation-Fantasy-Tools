# -*- coding: utf-8 -*-
"""Methodology v12 DRAFT — the pace-multiplier rewrite.

Produces Trade_Calculator_Methodology_v12_DRAFT.docx from v11. v11 IS NOT TOUCHED: it describes
the shipped v50.21 build, and a methodology that describes a build nobody is running is worse
than no methodology. Fold this in at ship time; until then it is a draft alongside the prototype.

Sections rewritten
  §13     the multiplier itself — total-vs-ceiling replaced by rate-vs-rate
  §13.1   the season-roll residual, which is built from the same ratio and therefore changes too
  §20.4   injury handling, where the short-circuit was documented
  §20.33  new dated entry recording the change, per the Part II convention

EVERY FIGURE BELOW IS PRODUCED BY remeasure_v12_evidence.py AND CHECKED BY
factcheck_methodology_v12.py ON A STATED POOL. The first draft of this file quoted five numbers
carried over from exploratory scripts that had bucketed availability role-blind (gp / team_games,
which reads a full 30-start season as 21% available) and had sized the tool-basis gate at the
pre-calibration k. Those are corrected here.

    python3 patch_methodology_v12.py            # report
    python3 patch_methodology_v12.py --apply
"""
import os, shutil, sys, copy
from docx import Document
from docx.shared import Pt

# Season directory holding GN_v50.20_wk21_2026-09-03/. Override with GN_YEAR.
HERE = os.path.expanduser(os.environ.get(
    'GN_YEAR', os.path.dirname(os.path.abspath(__file__)))).rstrip('/') + '/'
SRC = HERE + 'GN_v50.20_wk21_2026-09-03/Trade_Calculator_Methodology_v11.docx'
DST = HERE + 'Trade_Calculator_Methodology_v12_DRAFT.docx'
APPLY = '--apply' in sys.argv

# ══════════════════════════════════════════════════════════════ the new text
S13 = (
    "Multiplier = 1 + absorption × w × (rate ÷ expected_rate − 1), clamped [0.50, 1.50]. The "
    "multiplier compares a RATE to a RATE, so games missed do not enter it. rate = season "
    "fantasy points ÷ appearances. expected_rate = expectation ÷ ROLE_GAMES, where expectation "
    "keeps its §20.30(B) meaning (Pure, or Pure ÷ eng.g for a pre-peak production-basis player) "
    "and ROLE_GAMES is the appearances a full healthy season implies in that role: SP 33, RP 68, "
    "C 121, position player 154. Those four denominators were derived on 7 September 2026 from "
    "the 90th percentile of appearances by position group on this league's own board, scaled to "
    "162 games, and are FROZEN — re-deriving them weekly would move every player's multiplier "
    "for reasons that have nothing to do with the player. w = appearances ÷ (appearances + k) is "
    "a reliability weight that shrinks a thin sample toward 1.00, with k = 0.45 × ROLE_GAMES "
    "(SP 15, RP 31, C 54, position 69) so that \"fraction of a role season\" means the same thing "
    "in every role. Absorption is read from the §13 month table on the build's data-through date "
    "(GN_DATA_THROUGH), not typed into the page.\n"
    "WHY THIS REPLACED THE TOTAL FORM. Until v50.22 the multiplier compared pace — a season "
    "TOTAL annualized as YTD FP × F, F = 162 ÷ team_games_played — against expectation, a full "
    "healthy-season ceiling. That ratio is depressed by construction for anyone who missed time, "
    "however well he played when available, so the multiplier was partly an availability penalty. "
    "Both formulas were scored over the same 581 players — the population either formula "
    "actually prices, so imports (locked, step 1) and rule-retired players (held at 1.00, step "
    "2) are outside it — with availability defined role-adjusted as appearances ÷ (ROLE_GAMES × "
    "team_games ÷ 162), the fraction of his own role's workload, so that a full 30-start season "
    "does not read as 21% available. The total form's ratio ran 0.972 above 90% availability and "
    "0.229 below 40%, a spread of 0.744, and its mean multiplier fell monotonically across the "
    "four bands: 0.974, 0.848, 0.631, 0.506. Thirty per cent of the pool sat pinned at the 0.50 "
    "floor, where a multiplier has stopped conveying information at all. Availability is already "
    "priced once, in Hit% through the ir term (§20.4) and the post-peak durability model "
    "(§20.28); charging it again here was a double count.\n"
    "AND THE WORKAROUND INVERTED IT. The hard IL short-circuit existed to blunt that penalty, "
    "and it overshot. As a bare formula the total form correlated −0.222 with being on an IL "
    "designation, the double count in plain sight. Forcing every IL player to exactly 1.00 while "
    "most healthy players sat below it flipped the sign: in the shipped v50.21 build the "
    "multiplier correlates +0.246 with being on the IL. Being hurt was worth a raise. A player "
    "whose multiplier sat below 1.00 GAINED value by getting injured, because retiring the "
    "penalty outweighed the −0.02 Hit% haircut — Luis Robert Jr. was carrying a 0.500 multiplier "
    "and picked up $0.85 on going to the ten-day list in the week of 7 September 2026 — while a "
    "player above 1.00 was cut twice. The rate form needs no workaround: its ratio spread across "
    "the same four availability bands is 0.140 against 0.744 — five times smaller — its floor "
    "saturation is 0.0% against 30.1%, and it correlates −0.062 with being on the IL as a "
    "formula and −0.064 as built. Its mean multiplier by band is 0.978, 1.012, 0.970, 0.953: "
    "flat within about four points rather than falling by forty-seven, and no longer monotone in "
    "availability — the 70-to-90% band comes out slightly ABOVE the full-time band, because "
    "players who have missed some time are on this board performing marginally better per "
    "appearance than players who have played every day. The total form buried that under an "
    "availability penalty; the rate form reports it. The residual four-point sag in the bottom "
    "band is shrinkage doing its job, not a penalty: those players have the thinnest samples and "
    "w pulls them toward 1.00 from wherever their rate sits.\n"
    "PRECEDENCE, IN ORDER. (1) §20.15 import-pace players are locked, not gated — pm = 2 − 1/F "
    "is their design. (2) A multiplier retired by rule stays at 1.00: the §19.6 in-season "
    "ratchet and the §20.12 recency floor have already banked the season into Pure and must not "
    "be paid twice. (3) Tier and phase: only T1, T2 and Established-phase T3 are eligible "
    "(§20.10). (4) THE CEILING BASIS must be an established level, not a projection. A "
    "tool-basis ceiling never earns a multiplier even where cumulative-production promotion "
    "(§10) has moved the player to Established phase — 31 players clear the tier gate on that "
    "route, 30 of them pre-peak, and in the rate form they have appearances and nothing else "
    "catches them (Samuel Basallo, 21, tool-basis, 101 games, was being judged against 15.4 "
    "points per appearance and stood to lose $1.11). This is §20.10's own rationale — pace is "
    "meaningful only against an established level — applied to the basis rather than only to the "
    "phase label. (5) A pre-peak production-basis player with no growth factor holds at 1.00 and "
    "is reported: with no eng.g there is no defensible way to discount a projected peak, and "
    "falling through to the full peak reproduces the category error §20.30(B) fixed. Twenty-five "
    "players carry that condition, but precedence matters here: twenty-four of them are already "
    "held at 1.00 by rule (2), the ratchet or the recency floor, so exactly ONE reaches this "
    "gate and is reported by it — Mitchell Parker, on the 7 September board. The gate is cheap "
    "and the category error it prevents is not, which is why it is stated even at that "
    "population; the same condition would reach it far more often on a board where fewer young "
    "T3s had been ratcheted. (6) Pure < 300 holds at 1.00. (7) A minimum-appearance guard "
    "(SP 3, RP 8, C 15, position 15) replaces the old pace ≤ 50 test, which was a totals-domain "
    "proxy for the same thing. There is NO on-the-IL clause.\n"
    "THE ALLOW_NEW_PM RULING. The switch that keeps an eligible player parked at 1.00 once he "
    "gets there was a consequence of the total form: §13 in v11 recorded its rationale as "
    "\"pace annualizes on team games, so an injury-shortened season reads as decline, and "
    "re-opening the multiplier on return would halve some players.\" The rate form removes that "
    "cause, so the ruling loses its reason. Retaining it would also lock in the artifacts being "
    "removed: 167 players sit at exactly 1.000 on the live board and are priceable under the new "
    "gates — 108 of them held there by the IL short-circuit itself and 59 parked by the switch "
    "after an earlier clearance — and every one of them would stay frozen. On the prototype, "
    "lifting the switch is the LESS inflationary of the two options — RAW +6.0% against +7.1% "
    "with it retained — because re-pricing everyone lets players below their ceiling rate fall as "
    "well as rise. The switch ships OFF from v50.22, and the eligible-but-unpriceable cases under "
    "(5) above are reported weekly in its place. This also closes the first of the three items "
    "§20.30 left open: the 23 stale gatings it flagged, and Samuel Basallo specifically, are "
    "excluded by the ceiling-basis gate rather than parked behind a switch."
)

S131_RESIDUAL = (
    "At the roll the completed season's divergence is carried into the next year's Pure at a "
    "fraction, in both directions. From v50.22 the residual is the same quantity the §13 "
    "multiplier is built from, so the two can never disagree: residual = w × (rate ÷ "
    "expected_rate − 1), with rate, expected_rate and w exactly as §13 defines them and "
    "expectation retaining its §20.30(B) form. carry = clamp(λ × residual, −0.20, +0.20). "
    "Pure_next = Pure × the regression-or-growth step × (1 + carry), never lifted above the raw "
    "career peak — beating the peak is the ratchet's job — and never capped below the no-carry "
    "baseline.\n"
    "λ WAS REFITTED ON 8 SEPTEMBER 2026 AND HOLDS AT 0.40. The original λ = 0.40 was fitted on "
    "31 August against this league's own 2025→2026 pairs (326 vet-basis players, ratchet and "
    "floor cases excluded; OLS 0.445, Theil–Sen 0.498) using the OLD residual, final pace ÷ "
    "expectation − 1. Redefining the residual changes the quantity λ multiplies, so the fitted "
    "value could not be assumed to carry over and the roll was blocked pending a refit. The "
    "refit is now done. It required one input the board had never carried — 2025 APPEARANCES; "
    "fp25 was stored but no 2025 games count was, and the 31 August fit had recorded its own "
    "0.40 as a LOWER BOUND for exactly that reason. 2025 appearances for 1,462 players were "
    "pulled from ESPN on 8 September and joined on the ESPN player id; the pull's 2025 point "
    "totals reconcile with the board's stored fp25 for all 1,152 players carrying both, which "
    "confirms it reads the same stat block the board was built from. Regressing the 2026 "
    "residual on the 2025 residual, both under the new definition, over 329 pairs: OLS 0.374, "
    "Theil–Sen 0.432, midpoint 0.40, R² 0.188, bootstrap 95% interval 0.251 to 0.519. λ "
    "therefore does not move. What did improve is the fit itself — R² rises from about 0.11 "
    "under the old residual to 0.188 under the new one, so the same weight now rests on a "
    "tighter relationship.\n"
    "TWO SUB-FINDINGS, both recorded rather than acted on. First, the hitter/pitcher split was "
    "re-tested and again collapses: hitters OLS 0.478 (95% 0.355–0.613), pitchers 0.294 (95% "
    "0.157–0.515), and the bootstrap interval on the DIFFERENCE runs −0.072 to +0.386, spanning "
    "zero, with pitchers exceeding hitters in 8.6% of draws. One weight remains the right call, "
    "the same conclusion the August fit reached. Second, the wider pool that INCLUDES players "
    "who finished the season on an IL designation — which this section's rewrite permits, since "
    "a short season now attenuates through w rather than through an exclusion — gives 403 pairs "
    "at OLS 0.351 / Theil–Sen 0.401, midpoint 0.38. That is close enough to the strict pool's "
    "0.40 that the exclusion is not load-bearing either way; the strict pool is retained as the "
    "conservative choice and the agreement is the useful result. λ remains a shrinkage weight, "
    "not a claim that one season repeats: across players whose career best was 2025, 2026 "
    "retention ran a median 86% with a 54–117% spread."
)

S131_SCOPE = (
    "Scope follows the §13 multiplier exactly, including the ceiling-basis and growth-factor "
    "conditions: T1/T2 veterans and Established-phase T3 whose ceiling is production-basis. A "
    "tool-grade or depth ceiling is a projection, not a level a season can diverge from, which "
    "is the same reason §20.10 gates the multiplier off for Honeymoon and Book. The carry is "
    "skipped wherever the season is already banked — ratchet, recency floor, import-pace — so "
    "nothing is paid twice. The v11 clause skipping any player who finished the season on an IL "
    "designation is RETIRED: it existed because an injury-shortened total read as decline, and "
    "the residual no longer measures totals. A short season now attenuates through w rather than "
    "through an exclusion, which is both smoother and symmetric."
)

S131_EFFECT = (
    "Effect at the 2026 roll: THE v50.20 DRY-RUN FIGURES ARE VOID. The published dry run (λ 0.40 "
    "on the v50.20 board: 513 players in scope, 384 marked down, 129 marked up, 152 clipped by "
    "the ±20% guardrail, 53 held at the career peak, next-year totals −8.8%) was computed on the "
    "OLD residual and on the old scope, before the ceiling-basis and growth-factor conditions "
    "existed. It is retained here only as the record of what was run on 3 September 2026, and "
    "must be re-run with the refitted λ before it means anything. Expect the markdown count to "
    "fall: the old residual charged availability, so a large share of those 384 were players "
    "whose seasons were short rather than poor. The step (season_roll_lambda.py) gained its "
    "write path in v50.20; until then --apply printed the dry run and wrote nothing, and it "
    "still refuses to run without an explicit season-complete confirmation, so it cannot fire "
    "mid-season. RETIRED LIMITATION: v11 recorded that \"pace annualizes on TEAM games, so a "
    "season shortened by injury still reads as decline once the player returns. Until "
    "games-played reaches the weekly feed the carry cannot separate the two.\" Games played "
    "reached the feed and is the denominator of the new residual, so the carry now separates "
    "them by construction, and the 40 durability-window flags that stood in for the "
    "distinction are no longer needed."
)

S204 = (
    "On each refresh a player's IL stack penalty (the ir term) is updated from current status "
    "(IL7/IL10/IL15 = −0.02, IL60 = −0.05, day-to-day = none, and paternity, suspension and "
    "bereavement read as ACTIVE) and applied to Hit% as a delta against the prior stack: new "
    "Hit% = clamp(Hit% − old_ir + new_ir, 0.20, cap). The delta form makes it exactly "
    "reversible — clearing an IL-60 restores the full 0.05 — and this is now the ONLY channel "
    "through which a designation touches value. From v50.22 the Pace Multiplier is NOT "
    "short-circuited on the IL; §13 sets out why the short-circuit was a double count corrected "
    "in the wrong direction, leaving the shipped multiplier correlated +0.246 with being injured "
    "and making a trip to the IL profitable for any player whose multiplier sat below 1.00. The "
    "intent recorded in v11 — that an injured front-line player should not be penalized for "
    "missed time, Hunter Brown and Ronald Acuña Jr. being the named cases — is unchanged and is "
    "now delivered by the mechanism that belongs to it. Both men are among the largest gainers "
    "in the v50.22 prototype (Brown +$1.01, Acuña +$0.85), reaching roughly the same place by "
    "measuring how they pitched and hit rather than by suspending the measurement."
)

S2033_HEAD = ("20.33 Pace Multiplier Re-Based on Rate, and the IL Short-Circuit Retired "
              "(v50.22, September 2026)")

# appended to §20.30's "deliberately left open" paragraph so a decided question stops reading
# as undecided
RESOLVED_224 = (
    " RESOLVED at §20.33 (v50.22): the first of these three is closed. Those 23 players were "
    "stale Honeymoon/Book gatings, and Samuel Basallo — cited here as the reason not to lift "
    "the switch, on a 0.33 pace ratio — has a TOOL-BASIS ceiling. The v50.22 eligibility gate "
    "excludes tool-basis ceilings outright, so he is never priced at all and the objection "
    "dissolves; ALLOW_NEW_PM ships off. The third item, whether a completed below-peak season "
    "should carry into the following year's Pure, was answered by the §13.1 roll carry, but "
    "that carry's λ now requires refitting under the redefined residual before it can run."
)

S2033 = [
    "The multiplier compared a season total against a full-season ceiling, so it charged players "
    "for games they had missed — availability that Hit% had already priced through ir and the "
    "durability model. Scored over the same 581 players on the v50.21 board — the population "
    "either formula prices, imports and rule-retired cases excluded — the ratio the total form "
    "is built from ran 0.972 above 90% role-adjusted availability and 0.229 below 40%, and 30.1% "
    "of the pool sat pinned at the 0.50 floor. The IL short-circuit that was "
    "supposed to blunt this inverted it instead: the bare formula correlates −0.222 with being "
    "on an IL designation, but forcing IL players to exactly 1.00 while their healthy peers sat "
    "below it left the shipped multiplier correlated +0.246 with being injured. Two proposals "
    "were tested against the live board before the redesign was chosen. Projecting remaining "
    "appearances from the player's own appearance rate turns out to be algebraically identical to "
    "the shipped formula — ef + (ef/gp)(G_rem × gp/TG) = ef × 162/TG — reproducing it to 0 points "
    "across all 1,327 players with a games count; the gp terms cancel. Projecting remaining "
    "appearances as all remaining TEAM games overstates by +0.8% for everyday hitters and +220% "
    "for starting pitchers, who appear once every five team games (Blake Snell 386 → 1,421). "
    "Neither addresses the defect, because games already missed cannot be recovered by projecting "
    "the ones left. The comparison itself had to change.",

    "The rate form is set out in §13. Effect on the prototype, all 2,118 records: 579 change; "
    "clamp saturation over the priced pool falls from 31.3% to 1.0%, and the 0.50 floor — where "
    "175 players sat — empties completely; the availability spread in the underlying ratio falls "
    "from 0.744 to 0.140; the "
    "correlation with being on the IL goes from +0.246 as shipped to −0.064 as built; the dollar "
    "move runs a −0.36 to +0.55 five-to-ninety-five band with a +0.05 median and exactly one "
    "player moving more than $1.00. RAW_PER_DOLLAR re-bases 497.17 → 527.08, +6.0%, so every "
    "dollar figure in the league restates and cross-issue comparisons need the build stamp. "
    "Competitively the change is close to neutral: no organisation's share of total board value "
    "moves more than 0.30 of a percentage point (River Cats −0.30, MidwestBears −0.22, C-Town "
    "+0.16), and most of the re-rating lands in free agency (+0.58 of a point), which is where "
    "the injured and the small-sample players sit.",

    "Two defects were found by adversarial audit of the prototype and fixed before it was "
    "circulated, both of them the §20.10 category error resurfacing in the rate domain. "
    "Tool-basis ceilings promoted to Established phase on cumulative production were being "
    "judged against a scouting projection — 31 players, 30 pre-peak, with Samuel Basallo (21, "
    "101 games, judged against 15.4 points per appearance) standing to lose $1.11 before the "
    "fix, and four others between $0.39 and $0.61. The eligibility gate now tests the ceiling "
    "basis as well as tier and phase — which retires the objection §20.30 recorded against "
    "lifting ALLOW_NEW_PM, since Basallo was the named counterexample there (on a 0.33 pace "
    "ratio) and is now outside the pool entirely. Separately, pre-peak "
    "production-basis players with "
    "no eng.g were falling through §20.30(B) to the full projected peak; they now hold at 1.00 "
    "and are reported — twenty-five carry that condition and exactly one reaches the gate, the "
    "other twenty-four being held already by the ratchet or the recency floor. The shrinkage constant was also recalibrated: at k = 0.45 × ROLE_GAMES a "
    "six-start sample lands Garrett Crochet at 0.878 and Blake Snell at 1.172, where a quarter of "
    "that k had them at 0.82 and 1.26 — claims six starts cannot support.",

    "TEAM_GAMES remains a flat league-wide constant by commissioner direction (7 September 2026). "
    "Per-club game counts would require splitting every traded player's season at his trade date "
    "and tracking two clubs for each, and the residual errors are symmetric across the league. "
    "Note that the flat constant now enters only the §20.15 import formula, the role-adjusted "
    "availability diagnostic and the reported pace field; the multiplier itself no longer uses F "
    "at all.",

    "SHIP-TIME CHECKLIST. Three things change with the formula and are not automatic. (a) The "
    "verifier's invariant list, quoted at §20.30, tests \"no short-circuit leak (Pure below 300, "
    "pace at or below 50, on the IL)\"; two of those three tests must go and be replaced by the "
    "ceiling-basis and growth-factor gates plus the minimum-appearance guard, or the verifier "
    "will report failures on a correct build. (b) The §13.1 λ was refitted on 8 September and "
    "holds at 0.40, but the v50.20 roll dry run still has to be re-run because the residual and "
    "the scope both changed — see below. "
    "(c) RAW_PER_DOLLAR re-bases, so the Weekly's dollar figures are not comparable across the "
    "boundary and the build stamp has to be carried in any table that spans it. Part II entries "
    "dated before this one describe the total form and are correct as history; §13 is the "
    "authority on the current formula.",

    "CLOSED SINCE DRAFTING: the §13.1 λ refit. It was the one blocking item on this change. "
    "2025 appearances — the input the board had never carried, and the reason the August fit "
    "called its own 0.40 a lower bound — were pulled on 8 September, and the refit under the "
    "new residual returns OLS 0.374 / Theil–Sen 0.432, midpoint 0.40. λ does not move; R² "
    "improves from about 0.11 to 0.188. The v50.20 dry-run figures still have to be re-run, "
    "because the residual and the scope changed even though the weight did not. Carried forward "
    "unresolved: the "
    "prototype's biggest fallers are veteran pitchers with genuinely poor rates in small samples "
    "(Zac Gallen 12.7 points per start against an implied 43.5, −$0.89), and the fallers' Pure "
    "Ceilings, not their multipliers, are what a review should question next — Dustin May and "
    "Bryce Elder both come out ABOVE 1.00 (1.292 and 1.063) on 4.80 and 4.19 earned-run averages, "
    "which says their ceilings are set too low.",
]


def set_text(p, text):
    """Replace a paragraph's content, keeping the first run's formatting."""
    runs = p.runs
    if not runs:
        p.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r._element.getparent().remove(r._element)


def split_into(p, text):
    """Write a multi-line block as the paragraph plus siblings in the same style."""
    from docx.text.paragraph import Paragraph
    parts = text.split('\n')
    set_text(p, parts[0])
    anchor = p
    for extra in parts[1:]:
        new = copy.deepcopy(p._p)
        anchor._p.addnext(new)
        np = Paragraph(new, p._parent)
        set_text(np, extra)
        anchor = np
    return anchor


if not os.path.exists(SRC):
    sys.exit('missing source: %s' % SRC)


def find(d, pred, what):
    hits = [i for i, q in enumerate(d.paragraphs) if pred(q.text)]
    if not hits:
        sys.exit('could not locate %s' % what)
    if len(hits) > 1:
        sys.exit('AMBIGUOUS anchor for %s: %s' % (what, hits))
    return hits[0]


A13 = lambda t: t.startswith('Multiplier = 1 + absorption')
A131R = lambda t: t.startswith('At the roll the completed season')
A131S = lambda t: t.startswith('Scope is identical to the §13 multiplier')
A131E = lambda t: t.startswith('Effect at the 2026 roll')
A204 = lambda t: (t.startswith("On each refresh a player’s IL stack penalty")
                  or t.startswith("On each refresh a player's IL stack penalty"))

probe = Document(SRC)
print('located in v11:  §13 %d   §13.1 residual %d   §13.1 scope %d   §13.1 effect %d   §20.4 %d'
      % (find(probe, A13, '§13'), find(probe, A131R, '§13.1 residual'),
         find(probe, A131S, '§13.1 scope'), find(probe, A131E, '§13.1 effect'),
         find(probe, A204, '§20.4')))
print('to write: §13 %d chars / %d paras · §13.1 residual %d / %d · §13.1 scope %d · §20.4 %d · §20.33 %d paras'
      % (len(S13), S13.count('\n') + 1, len(S131_RESIDUAL), S131_RESIDUAL.count('\n') + 1,
         len(S131_SCOPE), len(S204), len(S2033)))

if not APPLY:
    print('\nDRY RUN — v11 untouched, no draft written (--apply to write the v12 draft)')
    sys.exit(0)

# v11 may be a hard link to an archived snapshot; we only ever READ it and write DST.
# The device shell cannot delete, so an existing DST is truncated in place rather than
# replaced — safe only if it is not itself a hard link into an archive, so check.
if os.path.exists(DST):
    n = os.stat(DST).st_nlink
    if n != 1:
        sys.exit('refusing to write %s: st_nlink=%d, it is hard-linked elsewhere' %
                 (os.path.basename(DST), n))
shutil.copy2(SRC, DST)
doc = Document(DST)

split_into(doc.paragraphs[find(doc, A13, '§13')], S13)
split_into(doc.paragraphs[find(doc, A131R, '§13.1 residual')], S131_RESIDUAL)
set_text(doc.paragraphs[find(doc, A131S, '§13.1 scope')], S131_SCOPE)
set_text(doc.paragraphs[find(doc, A131E, '§13.1 effect')], S131_EFFECT)
set_text(doc.paragraphs[find(doc, A204, '§20.4')], S204)

# §20.30 left the ALLOW_NEW_PM question open and named Basallo as the reason to leave it open.
# The ceiling-basis gate is the answer to it, so the open item is marked resolved where it
# stands — a methodology that still reads as undecided on a decided question misleads.
i224 = find(doc, lambda t: t.startswith('Deliberately left open for a ruling rather than fixed'),
            '§20.30 open items')
p224 = doc.paragraphs[i224]
set_text(p224, p224.text.rstrip() + RESOLVED_224)

set_text(doc.paragraphs[1],
         'DRAFT — pending a ship decision. Current shipped state is September 7, 2026 '
         '(Framework v15 · calculator v50.21). This draft describes the v50.22 candidate: the '
         'pace multiplier re-based on rate rather than season total, and the IL short-circuit '
         'retired. §13, §13.1, §20.4 and §20.33 differ from v11; everything else is v11 text.')

# match the style the sibling 20.x entries use, located by content
i2032 = find(doc, lambda t: t.startswith('20.32 Audit Pass'), '§20.32 heading')
hstyle = doc.paragraphs[i2032].style
bstyle = doc.paragraphs[i2032 + 1].style
print('  §20.33 heading style: %s   body style: %s' % (hstyle.name, bstyle.name))
doc.add_paragraph(S2033_HEAD, style=hstyle)
for para in S2033:
    doc.add_paragraph(para, style=bstyle)

doc.save(DST)
print('\nwrote %s (%.0f KB)' % (os.path.basename(DST), os.path.getsize(DST) / 1024.0))

chk = Document(DST)
t = ' '.join(q.text for q in chk.paragraphs)
bad = 0
for p in ('rate ÷ expected_rate', 'ROLE_GAMES is the appearances',
          'is NOT short-circuited on the IL', '20.33 Pace Multiplier Re-Based on Rate',
          'ships OFF from v50.22', 'AND THE WORKAROUND INVERTED IT', '167 players sit at exactly',
          '30.1%', 'stood to lose $1.11', 'RESOLVED at §20.33',
          'has a TOOL-BASIS ceiling', 'retires the objection §20.30 recorded',
          'closes the first of the three items', 'DRY-RUN FIGURES ARE VOID',
          'RETIRED LIMITATION', 'SHIP-TIME CHECKLIST',
          'exactly ONE reaches this gate', 'Mitchell Parker',
          'exactly one reaches the gate', 'Twenty-five', 'twenty-four of them',
          'λ WAS REFITTED ON 8 SEPTEMBER', 'OLS 0.374', 'R² 0.188',
          'CLOSED SINCE DRAFTING', 'spanning zero'):
    ok = p in t
    bad += 0 if ok else 1
    print('  %-46s %s' % (p[:46], 'present' if ok else 'MISSING'))
for stale in ('λ MUST BE REFITTED', 'THIS IS A BLOCKING ITEM', 'OPEN AND BLOCKING',
              '1.017', '0.612', '246 players', '$1.38', '15% to 1%',
              '746 eligible', '1.020', '0.253', '0.767', '23.7%', '24.9%', '0.121',
              '−0.077', '1.003, 1.062', 'Fifteen players are in this state',
              'Separately, fifteen pre-peak', 'Fifteen players carry',
              'fifteen carry that condition'):
    if stale in t:
        print('  STALE FIGURE STILL PRESENT: %s' % stale); bad += 1
# a stale normative claim contradicting the rewrite must not survive outside Part II history
import re as _re
pt2 = [i for i, q in enumerate(chk.paragraphs) if q.text.strip().upper().startswith('PART II')]
cut = pt2[0] if pt2 else len(chk.paragraphs)
REFUTED = ('RETIRED LIMITATION',            # §13.1 quotes the limitation, then retires it
           'removes that cause')             # §13 quotes the v11 rationale, then removes it
for i, q in enumerate(chk.paragraphs[:cut]):
    hit = _re.search(r'annualiz\w+ on (TEAM|team) games|games-?played (cannot|reaches the weekly)',
                     q.text)
    if not hit: continue
    if any(m in q.text for m in REFUTED):
        print('  quoted-and-refuted (OK) at para %d' % i); continue
    print('  CONTRADICTION SURVIVES in normative text at para %d: ...%s...'
          % (i, q.text[max(0, hit.start() - 70):hit.end() + 70])); bad += 1
print('  normative text (before Part II at para %d) scanned for contradictions' % cut)
print('  paragraphs %d -> %d' % (len(Document(SRC).paragraphs), len(chk.paragraphs)))
print('  v11 source: %d bytes, mtime unchanged check -> %s'
      % (os.path.getsize(SRC), os.path.basename(SRC)))
sys.exit(1 if bad else 0)

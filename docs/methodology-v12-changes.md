# Methodology v12 — which sections change

`research/patch_methodology_v12.py` produces `Trade_Calculator_Methodology_v12_DRAFT.docx` from
v11 without touching v11. v11 is deliberately left alone: it describes the build that is actually
running, and a methodology that describes a build nobody is running is worse than no methodology.

Run it against a directory containing `GN_v50.20_wk21_2026-09-03/Trade_Calculator_Methodology_v11.docx`:

```bash
python3 research/patch_methodology_v12.py            # dry run, locates the anchors
python3 research/patch_methodology_v12.py --apply
```

It locates every edit site by **content, not index**, refuses to run if any anchor is ambiguous,
scans the output for stale figures, and scans the normative text (everything before
`PART II — CHANGE LOG`) for claims the rewrite contradicts.

## Sections rewritten

| section | change |
|---|---|
| **§13** Pace Multiplier | the full rate-vs-rate formula, frozen `ROLE_GAMES`, the shrinkage rationale, the measured evidence, the seven-step precedence order including the two new gates, and the `ALLOW_NEW_PM` ruling |
| **§13.1** Season-Roll Carry | residual redefined as `w × (rate ÷ expected_rate − 1)`; the λ refit recorded as a **blocking** item; the v11 clause skipping players who finished on an IL designation retired; the v50.20 dry-run figures marked **void** and the "games-played is not in the feed" limitation retired |
| **§20.4** Injury Handling | the `ir` haircut becomes the sole injury channel; notes that Hunter Brown and Ronald Acuña Jr., the two players v11 named as the short-circuit's intended beneficiaries, are among the largest gainers under the replacement (+$1.01 and +$0.85) — reaching the same place by measuring how they pitched and hit rather than by suspending the measurement |
| **§20.33** (new) | the dated Part II entry: both rejected proposals, the measured effects, the two audit defects, the `k` recalibration, the flat-`TEAM_GAMES` direction, a ship-time checklist, and the blocking λ item |

## Two v11 open items closed in place

- **§20.30's ALLOW_NEW_PM question.** v11 left it open and named Samuel Basallo — on a 0.33 pace
  ratio — as the reason not to lift the switch. Basallo has a **tool-basis** ceiling, so the new
  ceiling-basis gate excludes him outright and the objection dissolves. Marked `RESOLVED at §20.33`
  where it stands, because a methodology that still reads as undecided on a decided question
  misleads.
- **§13.1's "known limitation."** v11 recorded that "pace annualizes on TEAM games, so a season
  shortened by injury still reads as decline… until games-played reaches the weekly feed the carry
  cannot separate the two." Games played reached the feed and is the denominator of the new
  residual, so the carry now separates them by construction.

## Fact check

`verify/factcheck_methodology_v12.py` re-derives every number and named player in the new text
from the live board and the prototype output. **PASS 64, FAIL 0.**

It exists because the first draft of §13 quoted five figures that did not survive scrutiny: the
availability bands had been bucketed role-blind (`gp ÷ team_games`, which reads a full 30-start
season as 21% available), the tool-basis gate had been sized at the pre-calibration `k`, and the
scoring pool had not excluded imports and rule-retired players. All five are corrected, and the
fact check is what keeps them corrected.

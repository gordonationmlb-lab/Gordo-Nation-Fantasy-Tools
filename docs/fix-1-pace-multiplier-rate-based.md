# Fix 1 — the pace multiplier, re-based on rate

Status: **prototyped and verified, not shipped. No open prerequisites** — the §13.1 λ was refitted
on 8 September 2026 and holds at 0.40 (see the README).
Methodology sections affected: §13, §13.1, §20.4, new §20.33.

## The defect

Until v50.22 the multiplier was

```
pace = round(ytd_fantasy_points × F),   F = 162 ÷ team_games_played
pm   = clamp(1 + absorption × (pace ÷ expectation − 1), 0.50, 1.50)
```

`pace` is a season **total** annualized on the number of games the *league calendar* has played.
`expectation` is a full healthy-season ceiling. A player who missed six weeks therefore fails that
comparison by construction, however well he played when he was available — the numerator is short
by the games he missed and the denominator is not.

Availability is already priced, twice deliberately and once by accident:

- `Hit%` carries the `ir` term for a current IL designation (§20.4).
- `Hit%` carries the post-peak durability model derived from IL history (§20.28).
- and then the multiplier charged for it again.

### Measured, on the 581 players either formula prices

Availability here is **role-adjusted** — `appearances ÷ (ROLE_GAMES × team_games ÷ 162)`, the
fraction of his own role's workload. This matters: the naive `gp ÷ team_games` reads a full
30-start season as 21% available and drops every starting pitcher into the bottom bucket, which
confounds role with health and was how the first draft of this analysis got the numbers wrong.

| role-adjusted availability | n | old ratio | old mean pm | new mean pm |
|---|---|---|---|---|
| > 90% | 170 | 0.972 | 0.974 | 0.978 |
| 70–90% | 141 | 0.828 | 0.848 | 1.012 |
| 40–70% | 155 | 0.537 | 0.631 | 0.970 |
| < 40% | 115 | 0.229 | 0.506 | 0.953 |

The old mean multiplier falls 47 points across that range. The new one holds within four.

- **Ratio spread** 0.744 → 0.140, five times smaller.
- **Clamp saturation** 31.3% → 1.0%, and the 0.50 floor goes from 175 players to zero.
- **Correlation with being on the IL**, as a bare formula: −0.222 → −0.062.

Note the new figures are not monotone: the 70–90% band comes out slightly *above* the full-time
band. That is a real property of this board — players who have missed some time are producing
marginally better per appearance than players who have played every day. The old form buried it
under an availability penalty. The residual four-point sag in the bottom band is shrinkage doing
its job, not a penalty: those players have the thinnest samples and `w` pulls them toward 1.00 from
wherever their rate sits.

### And the workaround inverted it

The hard IL short-circuit forced `pm = 1.00` for anyone on IL-7/10/15/60 or OUT. Since most healthy
players in the priced pool sat *below* 1.00 under the total form, pushing injured players up to
exactly 1.00 made the shipped multiplier correlate **+0.246** with being on the IL — the opposite
sign from the formula it was patching.

The consequence was perverse rather than merely wrong. A player whose multiplier sat below 1.00
**gained** value by getting hurt, because retiring the penalty outweighed the −0.02 `Hit%` haircut.
Luis Robert Jr. was carrying a 0.500 and picked up **$0.85** on going to the ten-day list in the
week of 7 September 2026. A player above 1.00 was cut twice.

## The replacement

```
rate          = season fantasy points ÷ appearances
expected_rate = expectation ÷ ROLE_GAMES
w             = appearances ÷ (appearances + k)
pm            = clamp(1 + absorption × w × (rate ÷ expected_rate − 1), 0.50, 1.50)
```

`expectation` keeps its §20.30(B) meaning — Pure, or Pure ÷ `eng.g` for a pre-peak
production-basis player. Absorption is read from the §13 month table on the build's
`GN_DATA_THROUGH` date, not typed in.

### ROLE_GAMES — frozen

| | SP | RP | C | POS |
|---|---|---|---|---|
| ROLE_GAMES | 33 | 68 | 121 | 154 |
| k = 0.45 × ROLE_GAMES | 15 | 31 | 54 | 69 |
| minimum appearances | 3 | 8 | 15 | 15 |

Derived 7 September 2026 from the 90th percentile of appearances by position group on this league's
own board, scaled to 162 games, and **frozen**. Re-deriving them weekly would move every player's
multiplier for reasons that have nothing to do with the player.

`k` is expressed as a fraction of ROLE_GAMES so that "a quarter of a role season" means the same
thing in every role. The fraction 0.45 was swept against a stated objective rather than picked: a
player with a quarter-role sample should not be able to move his own value by more than about
$0.50, and the small-sample tail should not dominate the movers list. At `k(SP) = 8` a six-start
sample put Garrett Crochet at 0.82 and Blake Snell at 1.26 — claims six starts cannot support. At
0.45 × ROLE_GAMES they land at 0.878 and 1.172, and clamp saturation fell from 6% to 1%.

### TEAM_GAMES stays flat

Commissioner direction, 7 September 2026: `TEAM_GAMES` remains a flat league-wide constant (143).
Per-club counts would require splitting every traded player's season at his trade date and tracking
two clubs for each, and the residual errors are symmetric across the league. Note the flat constant
now enters only the §20.15 import formula, the availability diagnostic and the reported `pace`
field — the multiplier itself no longer uses `F` at all.

## Precedence, in order

1. **§20.15 import-pace players are LOCKED**, not gated — `pm = 2 − 1/F` is their design.
2. **A multiplier retired by rule stays at 1.00** — the §19.6 in-season ratchet and the §20.12
   recency floor have already banked the season into Pure and must not be paid twice.
3. **Tier and phase** — T1, T2, and Established-phase T3 only (§20.10).
4. **The ceiling basis must be an established level, not a projection.** A tool-basis ceiling never
   earns a multiplier even where cumulative-production promotion (§10) has moved the player to
   Established phase.
5. **A pre-peak production-basis player with no growth factor holds at 1.00 and is REPORTED.**
6. **Pure < 300** holds at 1.00.
7. **A minimum-appearance guard** replaces the old `pace ≤ 50` test, which was a totals-domain
   proxy for the same thing.

**There is no on-the-IL clause.**

Gates 4 and 5 are new, and both were found by adversarial audit of the prototype rather than by
design. Both are the same §20.10 category error resurfacing in the rate domain.

- **Gate 4.** 31 tool-basis players clear the tier gate on the cumulative-production route, 30 of
  them pre-peak. In the total domain they were mostly hidden behind `pace ≤ 50` and the
  parked-at-1.00 ruling. In the rate domain they have plenty of appearances and nothing caught
  them: Samuel Basallo, 21, tool-basis, 101 games, was being judged against 15.4 points per
  appearance and stood to lose **$1.11**. This is §20.10's own rationale — pace is meaningful only
  against an established level — applied to the basis rather than only to the phase label.
- **Gate 5.** §20.30(B) divides the denominator by `eng.g` for a pre-peak production-basis player.
  With `eng.g` missing the code fell through to the full peak, which is the same category error.
  **25** players carry the condition; under the precedence order above only **one** actually
  reaches this gate (Mitchell Parker, on the 7 September board) — the other 24 are already held
  at 1.00 by rule 2, the ratchet or the recency floor. The gate is cheap and the category error it
  prevents is not, which is why it is stated even at that population.

## The ALLOW_NEW_PM ruling

The switch that kept an eligible player parked at 1.00 once he got there was a consequence of the
total form. v11 recorded its rationale as *"pace annualizes on team games, so an injury-shortened
season reads as decline, and re-opening the multiplier on return would halve some players."* The
rate form removes that cause.

Retaining it would also lock in the artifacts being removed: **167 players** sit at exactly 1.000
on the live board and are priceable under the new gates — 108 held there by the IL short-circuit
itself, 59 parked by the switch after an earlier clearance — and every one would stay frozen.

Lifting the switch is also the **less** inflationary of the two options, RAW +6.0% against +7.1%
with it retained, because re-pricing everyone lets players below their ceiling rate fall as well as
rise. **The switch ships off.** The eligible-but-unpriceable cases under gate 5 are reported weekly
in its place.

## Two proposals that were tested and rejected

Both were measured against the live board before the redesign was chosen.

**Project remaining appearances from the player's own appearance rate.** Algebraically identical to
the shipped formula:

```
ef + (ef/gp) × (G_rem × gp/TG)  =  ef × 162/TG
```

The `gp` terms cancel. Reproduced the shipped `pace` to **0 points across all 1,327 players** with
a games count.

**Project remaining appearances as all remaining TEAM games.** Overstates by +0.8% for everyday
hitters and **+220%** for starting pitchers, who appear once every five team games. Blake Snell's
pace goes 386 → 1,421.

Neither addresses the defect, because games already missed cannot be recovered by projecting the
ones left. The comparison itself had to change.

## What the applier rewrites

| field | how |
|---|---|
| `pm` | the precedence order above |
| `r` | `pc × pm × h` |
| `tjp` | scaled by the `pm` ratio — `tjp` is stored **pace-adjusted**, verified as `max(tjp) == pc × pm` for all 373 players carrying a multiplier off 1.00 |
| `tj` | `tjp[k] × Hit%(age + k)`, aged on the healthy-base bands per §20.30(A) |
| `RAW_PER_DOLLAR` | re-floated as the mean `r` over the eid-bearing `r > 0` pool |
| `d` | `round(r ÷ RAW, 2)` |
| `notes` | a dated `PACE v50.22` line per mover, with the reason |
| `GN_BUILD` | stamped `v50.22`, plus a `GN_PACE_BASIS = 'rate'` marker |

## Effect

- **579 multipliers change**, 318 up and 255 down.
- **RAW 497.17 → 527.08**, +6.0%. Every dollar figure restates; share-of-board is the honest lens.
- Dollar band −0.36 to +0.55 at the 5th/95th, median +0.05, **one** player over $1.00.
- No club's share of total board value moves more than **0.30 pp** (River Cats −0.30, MidwestBears
  −0.22, C-Town +0.16). Free agency absorbs +0.58 pp, which is where the injured and the
  small-sample players sit.
- Disclosure: C-Town Liquors, the commissioner's own club, is the largest gainer among the eight at
  +0.16 pp, driven by Acuña and Holliday coming off the 0.50 floor.

`data/pace_sample_by_mechanism.csv` has all 579 grouped by the mechanism that moved them —
floor released, IL unparked, re-priced down, re-priced up.

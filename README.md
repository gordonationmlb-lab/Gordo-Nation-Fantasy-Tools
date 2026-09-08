# Gordo Nation Calculator — v50.22 fixes

Two independent corrections to the Gordo Nation dynasty trade calculator, packaged with the
research that found them, the appliers that make them, and the verification that proves them.

Gordo Nation is a 16-team dynasty fantasy baseball league. The calculator prices every player on a
common risk-adjusted scale so trades can be argued about in dollars: `RA = Pure Ceiling × pace
multiplier × Hit%`, and `$ = RA ÷ RAW_PER_DOLLAR`. Both fixes below are to that middle term and to
how a prospect's ceiling is released as he matures. Section numbers (§13, §20.10, …) refer to the
league's own methodology document, which is not in this repo — `docs/` restates whatever a given
fix depends on.

| | fix | what it touches | who moves |
|---|---|---|---|
| **1** | [Pace multiplier re-based on rate](docs/fix-1-pace-multiplier-rate-based.md) | the `pm` field, and `r` / `tjp` / `tj` / `RAW_PER_DOLLAR` / `d` downstream | 579 multipliers |
| **2** | [Ceiling-fade release cap](docs/fix-2-ceiling-fade-release-cap.md) | the `fadeAdjustedTj` JavaScript only | 11 prospects, in the "Bust risk off" view |

Both were prototyped read-only against the live v50.21 board before any code was written. Neither
has been applied to a shipped build.

**Neither fix is blocked.** Fix 1's one prerequisite — the §13.1 season-roll λ refit — was
completed on 8 September 2026. λ holds at **0.40**; see [the λ section](#the-λ-refit-done).

---

## The short version

**Fix 1.** The pace multiplier compared a season *total*, annualized on team games, against a full
healthy-season ceiling. That ratio is depressed by construction for anyone who missed time, so the
multiplier was partly an availability penalty — and availability is already priced once, in `Hit%`
through the `ir` term and the post-peak durability model. Measured over the 581 players either
formula prices: the old ratio ran 0.972 at full availability and 0.229 below 40%, and 30% of the
pool sat pinned at the 0.50 floor, where a multiplier has stopped conveying information at all.

The IL short-circuit that was supposed to blunt this *inverted* it. As a bare formula the total
form correlated **−0.222** with being on the IL. Forcing every injured player to exactly 1.00 while
most healthy players sat below it flipped the sign, leaving the shipped multiplier correlated
**+0.246** with being injured. Being hurt was worth a raise: Luis Robert Jr. was carrying a 0.500
and picked up $0.85 by going on the ten-day list.

The replacement compares a rate to a rate, so games missed never enter it:

```
pm = clamp(1 + absorption × w × (rate ÷ expected_rate − 1), 0.50, 1.50)

  rate          = season fantasy points ÷ appearances
  expected_rate = expectation ÷ ROLE_GAMES         (§20.30(B) expectation)
  w             = appearances ÷ (appearances + k)   reliability weight
  ROLE_GAMES    = SP 33, RP 68, C 121, POS 154      FROZEN 2026-09-07
  k             = 0.45 × ROLE_GAMES = SP 15, RP 31, C 54, POS 69
```

**Fix 2.** The Ceiling-Fade switch releases a prospect's suppressors by dividing the stored
trajectory by the factors it believes are in the ceiling. One of those factors is scraped out of
the `notes` field by regex. `notes` is an **append-only log**, so a `blend 30/40/30` line written
before a later `GL REBUILD` survives it even though the rebuild replaced the ceiling outright.
Dividing by a factor that is not in the ceiling over-releases the player — Travis Sykora's released
Pure reached **2866** against a true ceiling of **1548**, so his seasons 5 through 10 all sat above
a ceiling he can never reach.

---

## Layout

```
patches/     the two appliers. Idempotent, dry-run by default, back up before writing.
verify/      everything that has to pass. verify_patched_build.py is the post-apply gate.
research/    how the defects were found and sized, including the two rejected proposals.
docs/        one document per fix, plus the methodology sections that change.
data/        the prototype's own output, kept as evidence. Point-in-time snapshots of the
             7 September 2026 board — every claim in docs/ is checkable against them, and the
             verify/ scripts re-derive rather than trust them.
```

## Applying

Both appliers take `--calc` and print a full report without writing anything. Add `--apply` to
write, or `--out` to write elsewhere. Each refuses to run twice.

```bash
CALC=path/to/GN_v50.22_.../calc/index.html

python3 patches/apply_pace_rate.py --calc "$CALC"            # read the report first
python3 patches/apply_pace_rate.py --calc "$CALC" --apply
python3 patches/apply_fade_cap.py  --calc "$CALC" --apply

python3 verify/verify_patched_build.py --calc "$CALC" \
        --baseline path/to/v50.21/calc/index.html
```

### Paths

The two appliers and `verify_patched_build.py` take an explicit `--calc`, so they need no setup.
Everything in `verify/` and `research/` reads the league season directory, which defaults to the
authoring environment's mount. Point it anywhere with `GN_YEAR`:

```bash
export GN_YEAR=~/leagues/gordo-nation/2026
python3 verify/verify_fade_anchor.py
```

`verify_fade_anchor.py` also honours `GN_CALC` to check one specific build.

Calculator builds are ~6 MB of generated HTML, so `.gitignore` keeps them out of the repo. This
repo holds the fixes, not the artifacts they produce.

### Notes on the appliers

`apply_pace_rate.py` checks its own invariants before writing and **exits without writing** if any
fail, so a bad run cannot produce a bad build. Order does not matter; fix 2 is pure JavaScript and
fix 1 is pure data, and they share no code path.

Run order for the verifiers:

```bash
python3 verify/verify_fade_anchor.py                      # fix 2, read-only, pre or post
python3 verify/verify_pm_rate_ship_readiness.py           # fix 1 against the prototype
python3 verify/verify_patched_build.py --calc "$CALC"     # both, standalone, post-apply
python3 verify/sample_pace_movers.py --csv                # who moved and why
```

## Verification status

Run against a v50.21 build with both fixes applied, 2026-09-08:

```
verify_patched_build.py     PASS 25   FAIL 0
verify_fade_anchor.py       PASS  5   FAIL 0
verify_pm_rate_ship_readiness.py  PASS 40  FAIL 0
factcheck_methodology_v12.py      PASS 64  FAIL 0
node --check on the patched page  OK
```

What the gate actually proves, rather than asserts:

- `r = pc × pm × h` and `d = round(r ÷ RAW, 2)` hold for all 2,118 records, and `RAW` is the mean
  `r` over the eid-bearing `r > 0` pool to the cent.
- Every eligible player's `pm` **recomputes exactly** from the published constants — nothing is
  hand-tuned.
- No multiplier survives any of the seven precedence gates it should not.
- `max(tjp) ≤ pc × pm` everywhere, with equality wherever the peak age falls inside the ten-year
  window (2,079 players; one 16-year-old is still rising at year 10).
- No T3/T4 release exceeds `max(pc, eng.tc × eng.sc) × pm`, before **or** after.
- The multiplier's correlation with being on the IL is −0.062, down from +0.246 as shipped.

## Effect

**Fix 1.** 579 multipliers change, 318 up and 255 down. `RAW_PER_DOLLAR` re-floats 497.17 → 527.08
(+6.0%), so every dollar figure in the league restates and share-of-board is the honest comparison.
The five-to-ninety-five dollar band is −0.36 to +0.55 with a +0.05 median and exactly one player
moving more than $1.00. Clamp saturation over the priced pool falls 31.3% → 1.0% and the 0.50 floor
empties completely. No club's share of total board value moves more than 0.30 of a percentage
point.

**Fix 2.** 11 prospects, all of whom were released above a ceiling they cannot reach. $59 of
ten-year value comes out of the fade view; two of the 11 are rostered. The default risk-adjusted
view is **not affected at all** — it reads the stored `tj` array and never enters the patched
function. A further 267 players shift by 1–3 RA points where the cap trims a rounding artifact of
integer-stored ceilings, worth $0.46 in total across all of them.

## The λ refit — done

**Refitted 8 September 2026. λ holds at 0.40.** This was fix 1's only open prerequisite, and it
gated the season roll rather than the calculator: λ is read by exactly one routine,
`season_roll_lambda.py`, which refuses to execute without `--apply --confirm-season-complete`.

λ = 0.40 was originally fitted on the *old* residual, `final pace ÷ expectation − 1`, which ran
from 0.972 at full availability down to 0.229 below 40%. The new residual,
`w × (rate ÷ expected_rate − 1)`, is flat within four points, so the fitted value could not be
assumed to transfer and had to be re-derived.

### What it needed, and where it came from

One input the board had never carried: **2025 appearances.** `fp25` (2025 points) was stored for
1,150 players; a 2025 games count for none — `gps` is games *started* in 2026. The August fit had
flagged this itself, calling its own 0.40 a lower bound because *"2025 games-played is not
available, so injury noise in the 2025 residual attenuates the slope."*

2025 appearances for **1,462 players** were pulled from ESPN's `kona_player_info` endpoint on
8 September, reading the `seasonId 2025, statSourceId 0, statSplitTypeId 0` stat block (statId 81
for batters, 32 for pitchers). The payload moved out of the browser in one 19,742-character
transfer verified byte-exact against a djb2 checksum. It is in `data/gp2025_2026-09-08.csv`, keyed
on ESPN player id.

**Validation before use:** the pull's own 2025 point totals reconcile with the board's stored
`fp25` for **all 1,152** players carrying both — zero disagreements. That confirms the pull reads
the same stat block the board was built from. `refit_lambda_v5022.py` performs this check itself
and refuses to fit if it fails.

### The fit

329 pairs — §13-eligible tier/phase, Pure ≥ 300, peak predating 2025, seasons already banked
elsewhere excluded. The August fit reported 326 on the same definition.

| | slope |
|---|---|
| OLS | 0.374 |
| Theil–Sen | 0.432 |
| **midpoint → λ** | **0.40** |
| R² | 0.188 (was ~0.11 on the old residual) |
| bootstrap 95% | 0.251 to 0.519 |

λ does not move. What improves is the fit underneath it: R² rises from about 0.11 to 0.188, so the
same weight now rests on a tighter relationship. `data/lambda_refit_2026-09-08.csv` has all 329
pairs so the fit can be re-audited.

### Two sub-findings, recorded rather than acted on

- **The hitter/pitcher split still collapses.** Hitters OLS 0.478 (95% 0.355–0.613), pitchers
  0.294 (95% 0.157–0.515). The bootstrap interval on the *difference* runs −0.072 to +0.386,
  spanning zero, with pitchers exceeding hitters in 8.6% of draws. One weight remains right —
  the same conclusion August reached.
- **The IL exclusion is not load-bearing.** The rewritten §13.1 permits including players who
  finished on an IL designation, since a short season now attenuates through `w`. That wider pool
  of 403 gives OLS 0.351 / Theil–Sen 0.401, midpoint 0.38 — close enough to 0.40 that the choice
  does not matter. The strict pool is retained as the conservative one, and the agreement is the
  useful result.

### Still to do before the roll

The v50.20 roll dry run (513 in scope, 384 marked down, −8.8%) must be **re-run**. Not because λ
moved — it didn't — but because the residual it multiplies and the scope it runs over both did.
Expect the markdown count to fall: the old residual charged availability, so a large share of
those 384 were players whose seasons were short rather than poor.

### Two smaller items, neither blocking

- The verifier's invariant list quoted at §20.30 tests `no short-circuit leak (Pure below 300,
  pace at or below 50, on the IL)`. Two of those three tests are obsolete and must be replaced by
  the ceiling-basis, growth-factor and minimum-appearance gates.
- `RAW_PER_DOLLAR` re-bases, so any Gordo Nation Weekly table spanning the boundary needs the build
  stamp carried with it.

## Known, not fixed here

The rate form makes a pre-existing Pure Ceiling miscalibration legible for the first time. Of the
31 players landing outside 0.65–1.35, **22 are "ceiling looks low"**, clustered hard in relievers
and depth free agents — Hayden Wesneski rates 40.4 points per start against a ceiling implying
15.4. In the other direction the cases are players whose Pure was anchored by a single monster
season and never came down, which is the ratchet asymmetry §20.30 already carries as open.

The multiplier is doing what it is told in every one of those cases. The number that is off is the
ceiling it is told to measure against, and that is a separate ruling.

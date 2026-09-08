# Changelog

## v50.22 — released 2026-09-08

Two independent fixes, both applied to all four HTML copies and shipped as
`GordoNation_Calculator_v50.22`. `RAW_PER_DOLLAR` 497.17 → 527.08.

### Changed

- **Pace multiplier re-based on rate.** `pm` now compares a per-appearance rate against the rate
  the ceiling implies, shrunk by a reliability weight, instead of comparing a season total against
  a full-season ceiling. Games missed no longer enter the multiplier.
  See `docs/fix-1-pace-multiplier-rate-based.md`.
- **The IL short-circuit is retired.** A designation now touches value through exactly one channel,
  the `ir` haircut on `Hit%` (§20.4). The short-circuit had left the shipped multiplier correlated
  +0.246 with being injured, making a trip to the IL profitable for anyone whose multiplier sat
  below 1.00.
- **`ALLOW_NEW_PM` ships off.** The switch that parked an eligible player at 1.00 was a consequence
  of the total form and loses its reason. 167 players were frozen at exactly 1.000 by it or by the
  short-circuit.
- **`RAW_PER_DOLLAR` re-floats 497.17 → 527.08** (+6.0%). Every dollar figure in the league
  restates. Cross-build comparisons need the build stamp.
- **Ceiling-fade release is capped.** `fadeAdjustedTj` no longer divides out a blend factor that
  the stored ceiling does not contain, and the release is hard-capped at
  `max(pc, eng.tc × eng.sc) × pm`. See `docs/fix-2-ceiling-fade-release-cap.md`.

### Applying

- Both appliers gained `--calc-dir`, which patches every HTML in a calc directory and bumps
  the service worker's cache name. A build ships `index.html` and `mobile.html` as two complete
  apps, and the distributed folder holds a second pair — four independent copies of the function.
  Patching one and checking another makes a working fix look broken.

### Added

- Two new precedence gates on the multiplier, both found by adversarial audit of the prototype:
  a **ceiling-basis** gate (a tool grade is not a level a season can diverge from) and a
  **growth-factor** gate (a pre-peak production-basis player with no `eng.g` holds at 1.00 and is
  reported).
- A **minimum-appearance guard** (SP 3, RP 8, C 15, POS 15) replacing the old `pace ≤ 50` test.
- `ROLE_GAMES` (SP 33, RP 68, C 121, POS 154) and `k = 0.45 × ROLE_GAMES`, both frozen.
- `GN_PACE_BASIS = 'rate'` marker in the build, so a build can be identified without inspecting
  the data.
- `blendInCeiling()` and `gnReleaseCap()` in the calculator.
- Standalone post-apply verification, `verify/verify_patched_build.py`.

### Resolved before release

- **§13.1's season-roll λ refit — DONE, 8 September 2026. λ holds at 0.40.** It was fitted on the
  old residual and could not be assumed to transfer, so the roll was blocked pending a refit.
  2025 appearances for 1,462 players were pulled from ESPN (the one input the board had never
  carried) and validated against the board's stored `fp25` — 1,152 of 1,152 agree. Refit over 329
  pairs: OLS 0.374, Theil–Sen 0.432, midpoint 0.40, R² 0.188 (up from ~0.11), bootstrap 95%
  0.251–0.519. The hitter/pitcher split was re-tested and again collapses. See
  `patches/refit_lambda_v5022.py` and `data/gp2025_2026-09-08.csv`.

### Still required before the roll runs

- **Re-run the v50.20 roll dry run.** Not because λ moved, but because the residual it multiplies
  and the scope it runs over both did.

### Not blocking, but required

- The verifier's invariant list (§20.30) still tests `pace ≤ 50` and `on the IL` as short-circuit
  leaks. Both are obsolete; replace with the ceiling-basis, growth-factor and minimum-appearance
  gates.
- Carry the build stamp on any Gordo Nation Weekly table spanning the RAW re-basing.

### Known, not fixed

- Pure Ceiling miscalibration, now legible: 22 of the 31 most extreme multipliers point at a
  ceiling set too low, clustered in relievers and depth free agents. The multiplier is correct in
  every one of those cases; the ceiling it measures against is not. Separate ruling.

## v50.21 — 2026-09-07

Data refresh. Engine unchanged from v50.20. Baseline for both fixes above.

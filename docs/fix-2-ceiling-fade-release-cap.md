# Fix 2 — the ceiling-fade release cap

Status: **prototyped and verified, not shipped.** No prerequisites.
Touches the `fadeAdjustedTj` JavaScript only. Found from a single question: *why are Travis
Sykora's seasons 5–10 all above his ceiling?*

## Two things were happening, and only one is a bug

**By design.** Sykora's displayed Pure Ceiling of 619 is not his ceiling — it is his ceiling
discounted for being in AA. His stored true ceiling is `eng.tc = 1548`, and `619 = 1548 × 0.40`,
the AA rung of the maturation ladder. The **Bust risk off** view (`FADE_MODE = 'on'`) implements
the 25 August commissioner ruling: release all three prospect suppressors — the scouting bust, the
maturation discount and the level-proximity penalty — one level per season up the promotion ladder.
So a trajectory climbing past 619 is exactly what that switch is for.

**The bug.** It should not climb past **1548**. It did, from season 5 on.

## Root cause

```js
const bd  = prospectBlend(player);
const mat = (e.matur != null && e.matur < 1) ? e.matur : 1.0;
...
const fadedPure = (player.tjp[yearIdx] / bd / mat) * bdFaded * matFaded;
```

The function recovers the "undiscounted" ceiling by dividing out the factors it believes are baked
into the stored trajectory, then re-applies faded versions. `mat` comes from `eng.matur`, which is
authoritative. `bd` comes from `prospectBlend()`, which **regex-scrapes the notes field**:

```js
const m = (player.notes || '').match(/blend\s+(\d+)\/(\d+)\/(\d+)/);
```

On Sykora that finds `SP/RP/Washout blend 30/40/30 → Pure ×0.54`.

That note is dead. A later `GL REBUILD v29` rebuilt his ceiling from scratch off the FanGraphs
grades (GNFV 57.3 → 1548) and the 0.54 blend is no longer a factor in it. But `notes` is an
**append-only log** — the rebuild replaced the ceiling without deleting the earlier line, so the
regex still finds it.

The arithmetic proves the blend is gone: `pc = 619` and `eng.tc × eng.matur = 1548 × 0.40 = 619.2`,
with no room for a third multiplier. Dividing by 0.54 anyway inflates the released ceiling by
**1.85×**.

### Sykora, as displayed

| | age | ladder stage | released RA | vs true ceiling 1548 |
|---|---|---|---|---|
| Current | 22 | AA | 366 | −1053 |
| Y2 | 23 | AAA | 617 | −793 |
| Y3 | 24 | Honeymoon | 916 | −466 |
| Y4 | 25 | Book | 1492 | −56 |
| **Y5** | 26 | Established | **2207** | **+932** |
| **Y6** | 27 | Established | **2551** | **+1318** |
| Y7–Y10 | 28–31 | Established | 2423 → 1949 | +1174 → +642 |

Released Pure peaks at **2866** against a true ceiling of 1548. Ten-year cumulative $34.08.

## The fix

Two changes, both additive. Nothing else in `fadeAdjustedTj` moves.

### 1. Ask the ceiling, not the prose

```js
function blendInCeiling(player) {
  const e = player.eng || {};
  const bd = prospectBlend(player);
  if (bd >= 0.999) return 1.0;                     // nothing to divide out
  const tc = e.tc;
  if (!tc || !player.pc) return bd;                // cannot test: keep prior behaviour
  const mat = (e.matur != null && e.matur < 1) ? e.matur : 1.0;
  const sc  = (e.sc != null) ? e.sc : 1.0;
  const tol = Math.max(1, 0.01 * player.pc);
  if (Math.abs(tc * mat * sc - player.pc)      <= tol) return 1.0;   // blend ABSENT
  if (Math.abs(tc * mat * sc * bd - player.pc) <= tol) return bd;    // blend PRESENT
  return bd;                                       // neither reconciles: prior behaviour
}
```

`eng.tc`, `eng.matur` and `eng.sc` pin down what the ceiling actually contains, so test it. The
two tests can never both fire — that would require `bd ≈ 1`, which the early return already
excludes. Verified: **0 ambiguous** across the 92 players carrying a scraped blend factor.

Classification: **83 keep** the blend (it really is in the ceiling), **9 drop** it.

### 2. A hard release cap

```js
function gnReleaseCap(player) {
  const e = player.eng || {};
  const tc = e.tc;
  if (!tc || !player.pc) return null;
  const sc = (e.sc != null) ? e.sc : 1.0;
  const pm = player.pm ? player.pm : 1.0;
  return Math.max(player.pc, tc * sc) * pm;
}
```

This is a guard, not the fix. It makes the invariant *a release never exceeds the ceiling a matured
prospect is scouted to reach* true by construction, so no future stale note can breach it again.

Every term is load-bearing:

- `eng.tc × eng.sc` is the ceiling a fully matured prospect is scouted to reach. **`eng.sc` is
  required** — position scarcity (C/2B/3B at 1.15) is applied *after* `eng.tc` is recorded, so 138
  players legitimately exceed a bare `eng.tc` by exactly 1.15×, 1.09× or 1.04×. Those are not bugs.
- **`pc` is a floor on the cap**, because `pc` sits *above* `eng.tc` for 15 players whose §19.6
  ratchet banked production past the original scouting grade. Releasing risk must never *subtract*
  value.
- **`× pm` is required** because `tjp` is stored pace-**adjusted**, not as raw Pure. Verified on
  the v50.21 board: `max(tjp) == pc × pm` for all 373 players carrying a multiplier off 1.00. The
  cap has to live in the same units as the quantity it bounds. (This one was wrong in the first
  draft of the patch and caught by the population test.)

## Who moves

11 players, all starting pitchers except none — all pitching prospects with a superseded blend
note, plus two whose stored ceiling reconciles against neither product.

| player | org | blend | pc | true cap | peak before | peak after |
|---|---|---|---|---|---|---|
| Travis Sykora | FA (WAS) | 0.540 | 619 | 1548 | 2866 | 1548 |
| Tyler Bremner | FA (LAA) | 0.540 | 422 | 1408 | 2605 | 1407 |
| Cam Caminiti | FA (ATL) | 0.540 | 397 | 1323 | 2451 | 1323 |
| **Hagen Smith** | **C-Town Liquors** | 0.640 | 861 | 1435 | 2242 | 1435 |
| **Kade Anderson** | **High Cheddar** | 0.860 | 1077 | 1795 | 2087 | 1795 |
| Jonah Tong | FA (NYM) | 0.820 | 819 | 1365 | 1665 | 1365 |
| Connor Prielipp | FA (MIN) | 0.800 | 930 | 1162 | 1453 | 1162 |
| Dax Fulton | FA (MIA) | 0.680 | 494 | 823 | 1211 | 823 |
| Carter Baumler | FA (TEX) | 0.800 | 436 | 726 | 908 | 726 |
| Andrew Alvarez | FA (WSH) | 0.760 | 634 | 726 | 793 | 726 |
| Luinder Avila | FA (KC) | 0.760 | 356 | 415 | 468 | 415 |

Only **two are rostered**: Hagen Smith (C-Town Liquors, $28.05 → $19.39) and Kade Anderson (High
Cheddar, $28.36 → $25.42).

## Scope and blast radius

- **The default risk-adjusted view is not affected at all.** It reads the stored `tj` array and
  never enters this function. Trade values in normal mode are unchanged.
- Of the 1,116 T3/T4 players the fade can act on: **838 byte-identical**, **267 rounding only**,
  **11 material**.
- The 267 shift by 1–3 RA points where the cap trims a rounding artifact — an integer-stored `pc`
  divided by a discount cannot reproduce `eng.tc` exactly. Total effect across all 267: **$0.46**.
- Every material change is a *reduction of an over-release*. Nothing gains.
- **Population invariant**: 11 players over their cap before, **0** after.

## What is deliberately not changed

`prospectBlend()` itself stays exactly as it is and remains reachable — `blendInCeiling()`
delegates to it. The fix is about *trusting* its answer, not about computing it differently. If a
future build starts writing `eng.bdisc` (which `prospectBlend` already prefers over the regex),
the whole question disappears and this fix becomes a no-op guard.

The 138 players who exceed a bare `eng.tc` by 1.15× / 1.09× / 1.04× are **untouched**. That is
position scarcity, correctly applied, and `eng.tc` simply excludes it.

# Hatch Havoc — Paper Gameplay Rules (Milestone 0)

**Status:** Milestone 0 deliverable (PRD v1.1 §27) — the authoritative rules
specification for the deterministic game model.
**Ruleset version:** 0.1.0
**Executable counterpart:** `prototype/gamecore-reference/` — this document and
that code MUST agree exactly. A change to either requires a matching change to
the other and a `RULESET_VERSION` bump if any golden replay hash changes.

Scope: the Milestone 0 core loop only — standard eggs, match-3, cluster
detachment, anchor-row insertion, walls, scoring, combo. Special eggs, hazard
eggs, and objectives are extension points (PRD §9, §8) specified in later
revisions.

---

## 1. Numeric model

All gameplay quantities are **Q16.16 fixed point**: a signed integer whose
value is `raw / 65536`. No floating point exists anywhere in the game model
(PRD §20.2).

| Operation | Definition |
|---|---|
| `fp_mul(a, b)` | `(a * b) >> 16`, arithmetic shift (floors toward −∞) |
| `fp_div(a, b)` | `floor((a << 16) / b)` — **floor**, not truncation |
| `fp_sqrt(a)` | `isqrt(a << 16)` — exact integer square root, `a ≥ 0` |

Constants:

| Name | Raw value | Meaning |
|---|---|---|
| `FP_ONE` | 65536 | 1.0 — also the egg diameter D |
| `FP_HALF` | 32768 | 0.5 — the egg radius R |
| `ROW_H` | 56756 | `floor(√3/2 · 65536)` — vertical row spacing |
| `CONTACT` | 55705 | `floor(0.85 · 65536)` — contact distance |
| `STEP` | 8192 | D/8 — ray-march step length |

## 2. Random number generator

**PCG32** (O'Neill), 64-bit wrapping state, standard `initseq` seeding, default
stream `seq = 54`. Verified against the published PCG32 reference output
(seed 42, seq 54 → `0xa15c02b7, 0x7b47f409, 0xba1d3330, …`). Bounded draws
use plain modulo (`next_u32() % bound`); the bias is irrelevant at these bound
sizes and keeps ports trivial.

RNG consumption order is part of the ruleset: draws occur only for
(a) the initial current egg, (b) the initial next egg, (c) each queue advance
after a shot, (d) each cell of a newly inserted anchor row, left to right.

## 3. Grid

Odd-r staggered hex grid (PRD §7.2):

- Rows `r = 0` (top, anchor row) downward; columns `c = 0` from the left.
- Board `parity ∈ {0, 1}`; a row's stagger is `s(r) = (r + parity) & 1`.
- Stagger-0 rows hold `width` cells; stagger-1 rows are shifted right half a
  diameter and hold `width − 1` cells. Adjacent rows always alternate stagger.
- Cell centers (Q16.16, D = 1.0):
  `x = (2c + 1 + s) · D/2`, `y = D/2 + r · ROW_H`.
- Neighbors of `(r, c)`, in the **fixed iteration order** used by every BFS —
  same-row left, same-row right, up-left, up-right, down-left, down-right:
  - stagger 0: `(r,c−1) (r,c+1) (r−1,c−1) (r−1,c) (r+1,c−1) (r+1,c)`
  - stagger 1: `(r,c−1) (r,c+1) (r−1,c) (r−1,c+1) (r+1,c) (r+1,c+1)`
  - candidates outside `0 ≤ c < rowWidth(s)` or `r < 0` are dropped.

## 4. Playfield geometry and shots

- The playfield is `width` diameters wide; side walls at `x = 0` and
  `x = width · D`. The moving egg is represented by its center; wall
  reflection happens at radius distance: bounds `[R, width·D − R]`.
- The launcher sits at `x = width·D/2`, `y = D/2 + (dangerRow + 2) · ROW_H`.
- A shot action is an aim vector `(dx, dy)` in Q16.16 with `dy < 0` (upward).
  `dy ≥ 0` or a zero vector is an invalid action.
- Trajectory: normalize the aim vector to a step of length `STEP = D/8`
  (`ux = fp_div(fp_mul(dx, STEP), len)`, likewise `uy`), then march:
  1. Advance `(x, y)` by `(ux, uy)`.
  2. If `x` crosses a wall bound, reflect (`x' = 2·bound − x`, negate `ux`)
     and increment the bounce counter.
  3. **Ceiling:** if `y ≤ R`, stop and snap (§5).
  4. **Contact:** if any occupied cell center is within `CONTACT` of `(x, y)`
     (compared as squared distances: `fp_mul(ddx,ddx) + fp_mul(ddy,ddy) <
     fp_mul(CONTACT, CONTACT)`), stop and snap.
- The step length D/8 with contact distance 0.85·D makes tunneling
  geometrically impossible.

## 5. Attachment (snap rule)

Candidate cells are, at any moment: every **empty anchor-row cell**, plus
every **empty valid cell adjacent to an occupied cell** (including cells in
the row just below the current bottom row). Sorted by `(row, col)`.

The stopped egg attaches to the candidate whose center has the **smallest
squared distance** to the stopped center; ties keep the earlier candidate in
`(row, col)` order. Because candidates are by construction empty and adjacent
to structure (or anchored), overlaps and floating attachments cannot occur
(PRD §7.3).

## 6. Per-shot resolution order

Fixed and deterministic (PRD §7.2). For each shot:

1. Resolve trajectory → snap cell.
2. Place the current egg in the snap cell.
3. **Match:** BFS the placed cell's same-color contiguous group (neighbor
   order §3; results sorted by `(row, col)`). If the group size ≥ 3, remove it.
4. **Detach:** BFS occupancy from all occupied anchor-row (`r = 0`) cells;
   every occupied cell not reached is floating — remove all floating cells.
5. **Score** (§8) and update combo.
6. **Win check:** if the board is empty → status `won`; skip steps 7–8.
7. **Danger advance** (§7).
8. **Loss check:** if any occupied cell has `r ≥ dangerRow` → status `lost`.
9. Advance the egg queue (current ← next; next ← RNG draw); increment the
   shot counter.

No rule consults wall-clock time, frame timing, or animation state (PRD §6.2).

## 7. Danger: anchor-row insertion (PRD §7.6)

- Each level/mode sets `shotsPerInsertion` `N` (`0` disables insertion).
- A countdown starts at `N` and decrements once per shot (step 7). At zero:
  - **Flip board parity.** Every existing row keeps its physical stagger and
    width as its index shifts down by one — this is the stable-identity rule.
  - **Prepend a new row 0** with stagger `s(0)` under the new parity, every
    usable cell filled with an RNG-drawn color from the level palette, left
    to right.
  - Reset the countdown to `N`.
- The presentation layer telegraphs insertion one shot ahead (Nest Keeper);
  presentation never feeds back into the model.

## 8. Scoring and combo (PRD §15)

Integer arithmetic only:

```
base      = 10 · matchedEggs + 20 · droppedEggs
bankMult  = 1 + min(bounces, 2)          (applied only when base > 0)
shotScore = base · bankMult · (4 + combo) // 4     (floor division)
```

- `combo` enters the shot at its pre-shot value (a streak's first scoring
  shot gets no bonus), then updates: `combo + 1` if the shot scored
  (`matched + dropped > 0`), else `0`.
- Dropped (detached) eggs score double matched eggs (PRD §7.2: detached
  clusters score more).
- A pure bank shot with no match/drop scores nothing and resets the combo.

## 9. Egg queue

`current` and `next` are drawn uniformly from the level's color palette via
the seeded RNG (consumption order §2). Restricting draws to colors still on
the board is a deliberate **non-rule** in ruleset 0.1.0 (noted as a tuning
candidate; changing it is a ruleset bump).

## 10. State, hashing, and replay

The complete logical state is: rows (color/empty per cell), parity, score,
combo, shot count, status (`active | won | lost`), insertion countdown,
current egg, next egg, RNG state + increment, seed, level id, ruleset
version. The canonical hash is sha256 over canonical JSON (sorted keys,
`,`/`:` separators) of that structure — field names in
`prototype/gamecore-reference/gamecore/replay.py`.

A run is exactly reproducible from `(level id, ruleset version, seed, ordered
action list)` — see `docs/hatch-havoc/replay-schema.md`. Golden vectors in
`prototype/gamecore-reference/golden/` are the conformance suite for any
port (PRD §24.3).

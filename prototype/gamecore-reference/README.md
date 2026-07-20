# Hatch Havoc — GameCore Reference Implementation

**Role:** executable rules oracle for the Hatch Havoc deterministic game model
(PRD v1.1 §6.2, §20). **This is not shipping code** — the product's GameCore
is Swift (PRD §20.1). This Python implementation exists to:

1. Prove the Milestone 0 core loop (shot → attach → match → detach → danger
   advance) is viable and fully deterministic.
2. Serve as the bit-exact specification the Swift port must reproduce —
   every numeric rule (Q16.16 arithmetic, PCG32, snap rule, resolution order)
   is defined here and in `docs/hatch-havoc/gameplay-rules.md`, which must
   stay in exact agreement with this code.
3. Generate **golden replay vectors** (`golden/*.json`) that the Swift
   GameCore's golden-replay test suite must match hash-for-hash (PRD §24.3).

Python 3.11+, standard library only — zero dependencies.

## Layout

```
gamecore/
  fixedpoint.py   Q16.16 arithmetic (bit-exact spec incl. floor-division rule)
  rng.py          PCG32 (verified against published reference output)
  hexgrid.py      odd-r staggered grid, neighbors, fixed-point cell centers
  board.py        occupancy, match BFS, anchor connectivity, row insertion
  shot.py         ray march, wall reflection, contact, snap rule
  scoring.py      match/drop/bank/combo scoring (integer)
  game.py         shot-indexed game loop + Level definition
  replay.py       canonical serialization, sha256 state hash, record/replay
levels/           example level definitions (docs/hatch-havoc/level-format.md)
golden/           golden replay vectors — regenerate with generate_golden.py
tests/            unittest suite incl. 100-seed randomized invariant test
```

## Running

```bash
cd prototype/gamecore-reference
python3 -m unittest discover -s tests        # full suite
python3 generate_golden.py                   # regenerate golden vectors
```

Regenerating goldens is byte-stable: running the generator twice produces
identical files. If a rules change alters any golden hash, bump
`RULESET_VERSION` in `gamecore/game.py` (PRD §8.4 seed/ruleset pinning) and
update `docs/hatch-havoc/gameplay-rules.md` in the same commit.

## Porting notes for Swift

- Use `Int64` for all Q16.16 values; `>>` is arithmetic in Swift (matches).
  Division must be **floor** division — Swift `/` truncates toward zero, so
  implement `floorDiv` explicitly (see `fixedpoint.py` docstring).
- PCG32 state math is wrapping 64-bit unsigned: use `&*` / `&+` on `UInt64`.
- The state hash is sha256 over canonical JSON (sorted keys, `,`/`:`
  separators, no whitespace) of the structure in `replay.canonical_state`.
  Reproduce the exact key names and value types.
- Iterate neighbors in the fixed order defined in `hexgrid.neighbors`; all
  returned cell lists are (row, col) sorted. Resolution order per shot is
  documented at the top of `game.py`.

## Explicit extension points (not implemented here — post-M0)

Special eggs (Wild/Blast/Crack), hazard eggs, objectives beyond clear-all,
move limits, and assist modifiers. Each slots into the resolution order at
step 3–4 (see `game.py` docstring) and must keep every transition a pure
function of (state, action, seed).

# Hatch Havoc — Level Definition Format (v1)

**Status:** Milestone 0 deliverable (PRD v1.1 §35 step 10; schema fields per §21.1)
**Examples:** `prototype/gamecore-reference/levels/level-001.json`, `level-002.json`
**Loader:** `gamecore/game.py` → `Level.from_dict` (reference core reads the
subset it implements; unknown sections are ignored by the loader but reserved
by this spec).

Levels are JSON documents. All fields are required unless marked optional.

```jsonc
{
  "id": "ref-001-first-clutch",        // unique, stable, kebab-case
  "environment": "fern-canyon",        // environment theme key (PRD §13.2)

  "board": {
    "width": 8,                        // cells in an unstaggered row (>= 2)
    "parity": 0,                       // initial stagger parity (0 or 1)
    "rows": [                          // top row first; '.' = empty cell
      "RRGGBBYY",                      // stagger-0 rows: exactly <= width chars
      "RGGBBYY",                       // stagger-1 rows: <= width - 1 chars
      "..GB...."
    ]
  },

  "colors": ["R", "G", "B", "Y"],      // palette for this level (4-6, PRD §9.1)

  "danger": {
    "dangerRow": 10,                   // loss when any occupied row index >= this
    "shotsPerInsertion": 0             // anchor-row insertion cadence; 0 = off (§7.6)
  },

  "objectives": [                      // reserved: reference core implements
    {"type": "clearAllEggs"}           // clearAllEggs implicitly; full objective
  ],                                   // system is a post-M0 extension (PRD §8.1)

  "limits": {"shots": 0},              // 0 = unlimited; reserved post-M0

  "eggSequence": {"policy": "seededUniform"},  // only policy in ruleset 0.1.0

  "seedPolicy": {
    "mode": "fixed",                   // "fixed" (authored levels) | "daily"
    "seed": 12345                      // required when mode == "fixed"
  }
}
```

## Rules

- **Row strings** use single-character color keys from `colors`, `'.'` for
  empty. A row string may be shorter than its usable width; missing trailing
  cells are empty. A string longer than the row's usable width is a
  validation error.
- **Color keys** are opaque identifiers. Display color, accessibility pattern
  overlay (PRD §17.1), and localization live in the egg definition catalog
  (PRD §21.2), never in level files.
- **`seedPolicy.mode: "daily"`** means the seed is derived from the canonical
  daily boundary (PRD §8.4) and the level is a Daily Eruption board; such a
  level must also be pinned to a `rulesetVersion` at publication time.
- **Versioning:** breaking changes to this format bump the format version in
  the filename convention (`level-format.md` → v2) and require a loader
  migration; levels themselves are immutable once shipped (fixes are new
  level ids).

## Reserved sections (specified post-M0)

`specialEggs`, `hazards`, `assistOverrides`, `tutorialPrompts`, `rewards` —
field shapes per PRD §21.1; they must not affect ruleset 0.1.0 replay hashes
until implemented behind a ruleset bump.

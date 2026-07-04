---
id: P4-09
title: Consolidated LLM-security red-team regression suite
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: [P3-05, P4-06, P4-07]
live_validation: false
---

## Context

Across the roadmap, individual tasks add adversarial cases under `tests/redteam/`.
This task consolidates them into a coherent, documented **standing regression
gate** so LLM-security defenses can't silently regress, and gives Codex a single
place to grow the corpus over time.

## Scope

**In:**
- A `tests/redteam/` package with shared fixtures/utilities (injection corpus,
  LLM stub helpers) and clear categories mapped to the README RT-1..RT-7 taxonomy.
- A `pytest -m redteam` marker (or subdir target) to run the suite in isolation.
- A short `tests/redteam/README.md` describing coverage + how to add a case.

**Out:** New defenses (those live in their feature tasks).

## Files

- `tests/redteam/__init__.py`, `conftest.py`, `corpus.py` (new).
- `tests/redteam/README.md` (new).
- Consolidate/relocate existing red-team tests from earlier tasks.
- `pytest.ini` / `pyproject` — register the `redteam` marker.

## Implementation steps (Builder / Sonnet)

1. Create the package + shared injection corpus + LLM-stub helpers.
2. Move earlier tasks' red-team tests under it; map each to an RT category.
3. Register the marker; ensure `pytest -m redteam` runs green.
4. Document coverage matrix (RT-1..RT-7 → tests) and the "add a case" recipe.

## Testing requirements

**Unit/redteam:** full `tests/redteam` suite green; coverage matrix has no empty
RT rows for surfaces that exist.
**Live:** none.

## Acceptance criteria

- [ ] `tests/redteam/` package with shared corpus + helpers.
- [ ] `pytest -m redteam` runs the suite in isolation, green.
- [ ] Coverage matrix (RT-1..RT-7) documented; gaps called out as follow-ups.
- [ ] Full suite green (count recorded).

## Red-Team Checklist (Codex)

> Mode: llm-surface. Codex owns growing this corpus — treat gaps as findings.
- [ ] Each RT category with a live surface has at least one meaningful case.
- [ ] Corpus includes encoding/obfuscation/multilingual injection variants, not
      just the obvious English "ignore previous instructions".
- [ ] Suite is deterministic (stubbed LLM) so it can gate CI.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: n/a

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

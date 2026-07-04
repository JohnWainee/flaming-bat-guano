---
id: P<phase>-<NN>
title: <short imperative title>
phase: <2|3|4>
status: todo            # todo | in_progress | ready_for_redteam | red_teaming | changes_requested | approved | done | blocked
builder: sonnet
redteam_by: codex
redteam: llm-surface     # llm-surface | security-review
depends_on: []           # list of task ids or paths that must be `done` first
live_validation: false   # true if any acceptance step needs real Azure/SNOW/Qdrant/Exchange/Bot Framework
---

## Context

<Why this task exists; the one-paragraph "so that". Link the phase goal.>

## Scope

**In:**
- <bullet>

**Out (explicitly not this task):**
- <bullet>

## Files

- `path/to/file.py` — <what changes>
- `tests/...` — <tests to add>

## Implementation steps (Builder / Sonnet)

1. <concrete step>
2. <concrete step>

## Testing requirements

**Unit (must pass in CI, no external services):**
- <case>

**Live validation (gated on creds/env — record evidence or defer with reason):**
- <case, or "none">

## Acceptance criteria

- [ ] <verifiable outcome>
- [ ] Unit tests added; full suite green (record count in Test Evidence)
- [ ] Docs updated if behavior/config changed

## Red-Team Checklist (Codex)

> Mode: `llm-surface`. Draw applicable items from README canonical list + task-specific.
- [ ] RT-1 Direct prompt injection — <task-specific angle>
- [ ] RT-<n> ...

<For `security-review` mode, replace with Security-Review Criteria bullets.>

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- YYYY-MM-DD — <agent> — <status change / note>

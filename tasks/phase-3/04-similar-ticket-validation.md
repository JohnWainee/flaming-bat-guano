---
id: P3-04
title: Validate similar-ticket finder on real data
phase: 3
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: [P3-03]
live_validation: true
---

## Context

The chatbot surfaces a "similar past ticket" heads-up during intake
(`_fetch_similar_suggestion`, score > 0.85) and the dashboard has a similar-ticket
finder. Validate the threshold and UX on real data so suggestions are helpful,
not noisy or misleading — and never leak another user's ticket inappropriately.

LLM-surface: suggestions are shown to end users mid-conversation.

## Scope

**In:**
- Tune/confirm the similarity threshold against labeled pairs.
- Confirm the intake suggestion fires only when genuinely relevant.
- Confirm dashboard similar-ticket results are ranked sensibly.

**Out:**
- Trend analysis (P3-05).

## Files

- `services/orchestrator/conversation/state_machine.py` — threshold only if tuning needed.
- `services/dashboard/app.py` — similar-ticket panel tweaks if needed.
- `tests/test_conversation.py` — unit-test suggestion gating (mock vector client).
- `docs` — chosen threshold + rationale.

## Implementation steps (Builder / Sonnet)

1. Unit-test `_fetch_similar_suggestion` gating: fires above threshold, silent
   below, swallows vector errors (mock the client).
2. Live: sample intake flows; confirm precision of the heads-up.
3. Live: eyeball dashboard similar results on real tickets.

## Testing requirements

**Unit:** suggestion gating + error-swallowing behavior.
**Live (gated):** threshold validated on labeled pairs; record decision.

## Acceptance criteria

- [ ] Suggestion gating unit-tested.
- [ ] Threshold validated on real data (or deferred w/ reason).
- [ ] Dashboard similar-ticket results sane on real data.
- [ ] Unit suite green (count recorded).

## Red-Team Checklist (Codex)

> Mode: llm-surface. Cases under `tests/redteam/test_similar_leak.py`.
- [ ] RT-3/RT-4 — a similar-ticket suggestion during intake must not disclose
      another user's confidential ticket content beyond the non-sensitive
      reference (number/type), and must respect any access scope.
- [ ] RT-2 — an injected string in a historical ticket can't turn the suggestion
      line into attacker-controlled instructions rendered to the user.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

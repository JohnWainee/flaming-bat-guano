---
id: P2-01
title: Render Teams Adaptive Card at the CONFIRM step (Edit/Confirm)
phase: 2
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: [P2-00]
live_validation: true
---

## Context

Today the CONFIRM step returns a markdown text summary and waits for the user to
type "yes". In Teams we can present a structured **Adaptive Card** with the
collected fields and **Confirm**/**Edit** buttons, reducing mis-submits and
mis-parsed confirmations. This is the last open Phase 2 item.

LLM-surface: the card is populated from LLM-extracted field values and its button
actions drive a real SNOW `create`. The confirmation gate must stay
user-explicit and un-spoofable.

## Scope

**In:**
- A card builder that turns `(ticket_type, collected_fields)` into an Adaptive
  Card JSON payload, using `display_value()` for human-readable coded fields.
- `teams_bot` renders the card when the orchestrator reply indicates
  `stage == CONFIRM`; handles the `Action.Submit` callback for Confirm/Edit.
- Confirm → sends a canonical confirm message to `POST /chat`; Edit → returns the
  user to field collection for the chosen field.
- Card templates live in `services/teams_bot/cards/`.

**Out:**
- Email surface (email stays text-based).
- Rich cards for stages other than CONFIRM.

## Files

- `services/teams_bot/cards/confirm_card.py` (new) — pure builder
  `build_confirm_card(ticket_type, fields) -> dict`.
- `services/teams_bot/cards/confirm_card.json` (new) — template/skeleton.
- `services/teams_bot/main.py` — detect CONFIRM stage; send card; handle
  `activity.value` submit actions.
- `services/orchestrator/main.py` — ensure `/chat` response exposes enough
  (`stage`, fields) for the bot to build the card; add if missing.
- `tests/test_teams_cards.py` (new) — pure builder tests (no Bot Framework).

## Implementation steps (Builder / Sonnet)

1. Write `build_confirm_card` as a **pure function** (no botbuilder import) so it
   unit-tests without the SDK — mirror the `email_ingestor/processing.py` pattern.
2. Map each collected field to a card `FactSet` row via `display_value()`; add
   `Action.Submit` buttons carrying `{"action": "confirm"}` /
   `{"action": "edit", "field": <name>}`.
3. In `teams_bot`, when the orchestrator reply has `stage == "confirm"`, send the
   card instead of text. On an inbound activity with `activity.value`, translate
   the action into the appropriate `/chat` message.
4. Keep a text fallback for non-Teams / card-unsupported clients.
5. Add unit tests for the builder; run the suite.

## Testing requirements

**Unit (no SDK):**
- `build_confirm_card` includes every collected field, renders coded values as
  labels (urgency "2" → "High"), and emits exactly one confirm + N edit actions.
- Malformed/empty fields don't raise.

**Live validation (gated on Bot Framework + Teams):**
- Card renders in a real Teams chat; Confirm creates the ticket; Edit returns to
  collection. Record transcript/screens or defer with "no Bot Framework env".

## Acceptance criteria

- [ ] `build_confirm_card` is pure and unit-tested.
- [ ] CONFIRM replies render as a card in Teams; text fallback preserved.
- [ ] Confirm button submits; Edit button re-collects the named field.
- [ ] Coded fields shown as human labels via `display_value()`.
- [ ] Unit suite green (count recorded); live validation done or deferred w/ reason.
- [ ] `CLAUDE.md` Phase 2 line updated; `cards/` no longer empty.

## Red-Team Checklist (Codex)

> Mode: llm-surface. Add regression cases under `tests/redteam/test_confirm_card.py`.
- [ ] RT-1 — a crafted field value containing card/markup or `Action` JSON cannot
      inject new actions or alter the confirm semantics (card is data, not code).
- [ ] RT-1 — LLM-extracted text in a field cannot smuggle a second hidden submit
      action or auto-trigger confirm without a click.
- [ ] RT-6 — the submit callback verifies the acting user matches the
      conversation's `user_id` (no confirming someone else's draft in a group chat).
- [ ] RT-5 — Edit action's `field` value is validated against the ticket type's
      known fields (no arbitrary field injection into state).
- [ ] RT-7 — field values are escaped/encoded for Adaptive Card text blocks; no
      markup/link injection rendered as trusted.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

---
id: P4-00
title: PII-safe structured logging + correlation ids
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P2-00]
live_validation: false
---

## Context

Production needs traceable, structured logs with a correlation id threaded across
orchestrator → SNOW/LLM/vector calls, **without** logging message bodies, ticket
PII, or secrets. Foundational for metrics and incident debugging.

## Scope

**In:**
- Structured (JSON) logging config; per-request correlation id (accept inbound or
  generate) propagated through the call chain.
- A redaction helper ensuring bodies/PII/secrets never hit logs.
- Convert existing `logger` calls to the safe pattern where they currently risk
  leaking content.

**Out:** Prometheus (P4-01), Grafana (P4-02).

## Files

- `services/orchestrator/logging_setup.py` (new).
- `services/orchestrator/main.py` — middleware assigns/propagates correlation id.
- Audit `snow/client.py`, `state_machine.py`, `email_ingestor/main.py` for body/PII logging.
- `tests/test_logging.py` (new) — redaction + correlation-id unit tests.

## Implementation steps (Builder / Sonnet)

1. Add JSON log formatter + correlation-id contextvar + FastAPI middleware.
2. Add `redact()` and route sensitive values through it; grep for existing
   `%s` logs that include message/body/field content and fix.
3. Unit-test that redaction removes known-sensitive patterns and correlation id
   appears on records.

## Testing requirements

**Unit:** redaction masks emails/tokens/bodies; correlation id present + stable per request.
**Live:** none.

## Acceptance criteria

- [ ] Structured logs with correlation id across the request lifecycle.
- [ ] No message bodies / PII / secrets in logs (verified by test + audit).
- [ ] Unit suite green (count recorded).
- [ ] `.env.example` documents log-level/format settings.

## Security-Review Criteria (Codex)

- [ ] No code path logs raw user message, ticket description, credentials, or
      OAuth tokens at any level.
- [ ] Correlation id is not a vector for injection into log tooling (sanitized).
- [ ] Redaction can't be trivially bypassed by field nesting/encoding.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: n/a

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

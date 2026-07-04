---
id: P4-05
title: Rate limiting + retry/dead-letter in the orchestrator
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P2-00]
live_validation: false
---

## Context

Phase 4 hardens for production. The orchestrator calls Azure OpenAI and
ServiceNow synchronously with no backpressure or failure isolation: a burst of
Teams/email traffic, or a flaky SNOW instance, can exhaust upstream quotas or
wedge conversations. This task adds per-user rate limiting and a retry +
dead-letter path for outbound SNOW/LLM calls.

This is **not** an LLM-surface task in the red-team sense — no new model output
reaches a user or an action. It carries **Security-Review Criteria** instead.

## Scope

**In:**
- Token-bucket rate limit per `user_id` (and a global ceiling) on `POST /chat`
  and `POST /email`; configurable via settings; 429 with `Retry-After` when
  exceeded.
- Bounded retry with exponential backoff + jitter for SNOW `create` and LLM
  calls; on terminal failure, write the payload to a dead-letter store (Redis
  list or disk under `/data/`) with enough context to replay.
- A minimal replay/inspect entry point for the dead-letter queue.

**Out:**
- Prometheus metrics (separate Phase 4 task).
- Horizontal pod autoscaling (separate Phase 4 task).

## Files

- `services/orchestrator/ratelimit.py` (new) — token-bucket, backed by Redis.
- `services/orchestrator/deadletter.py` (new) — enqueue/inspect/replay.
- `services/orchestrator/main.py` — apply the limiter to the two POST routes.
- `services/orchestrator/snow/client.py` — wrap `create_ticket` with retry +
  dead-letter on terminal failure.
- `shared/config.py` — `RATE_LIMIT_*`, `RETRY_*`, `DEAD_LETTER_*` settings.
- `tests/test_ratelimit.py`, `tests/test_deadletter.py` (new).

## Implementation steps (Builder / Sonnet)

1. Implement the token bucket against Redis (atomic via Lua or `INCR`+`EXPIRE`);
   fail-open only if explicitly configured, else fail-closed on Redis outage.
2. Add FastAPI dependency that enforces per-user + global limits, returns 429 +
   `Retry-After`.
3. Wrap SNOW create (and LLM calls) with backoff+jitter; on exhaustion, enqueue
   to dead-letter with payload + error + timestamp + correlation id.
4. Add a replay function that re-submits a dead-letter entry and removes it on
   success.
5. Unit-test bucket math (allow/deny across a window), 429 shaping, retry count,
   and dead-letter enqueue/replay. Use fakeredis or a Redis stub.

## Testing requirements

**Unit:**
- Bucket allows N then denies within window; refills after TTL.
- Retry stops at the configured max and dead-letters exactly once.
- Replay removes the entry on success, retains on failure.

**Live validation:**
- none (deterministic with a Redis stub).

## Acceptance criteria

- [ ] Per-user + global limits enforced; 429 + `Retry-After` on exceed.
- [ ] SNOW/LLM calls retry with backoff+jitter; terminal failures dead-lettered.
- [ ] Dead-letter entries are replayable and self-describing.
- [ ] Behavior configurable via settings; safe defaults documented in `.env.example`.
- [ ] Unit suite green (count recorded).

## Security-Review Criteria (Codex)

> Mode: security-review (no LLM surface). Verify:
- [ ] Rate-limit keys derive from an authenticated `user_id`, not a spoofable
      client-supplied header — a caller can't reset their bucket by forging id.
- [ ] Redis outage fails **closed** by default (no unlimited bypass); fail-open
      only when explicitly configured.
- [ ] Dead-letter payloads don't persist secrets/credentials; PII in stored
      bodies is scoped and TTL'd, not retained indefinitely in plaintext.
- [ ] Replay path is not exposed as an unauthenticated endpoint.
- [ ] Backoff has jitter (no synchronized retry storm / self-DoS).

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: deferred (deterministic with stub)

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

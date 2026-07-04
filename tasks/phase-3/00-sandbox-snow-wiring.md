---
id: P3-00
title: Wire sandbox ServiceNow + connection smoke test
phase: 3
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P2-00]
live_validation: true
---

## Context

Phase 3 validates the ingestion + dashboard against real data. Before anything
else we need a working, least-privilege connection to a sandbox/dev ServiceNow
instance and a smoke test that proves auth (basic **and** OAuth paths) and table
read access without mutating anything.

Not an LLM surface — carries Security-Review Criteria.

## Scope

**In:**
- A read-only smoke-test entry point that authenticates and issues a bounded
  `GET` against each required table (`incident`, `sc_request`, `sc_req_item`,
  `change_request`, `problem`) with `sysparm_limit=1`.
- Confirm both `snow_auth_method` values work against the sandbox.
- Document the minimum SNOW role/ACLs required for read.

**Out:**
- Any write to SNOW. Any bulk pull (that's P3-01).

## Files

- `services/ingestion_pipeline/smoke_test.py` (new) — connect + 1-row read per table.
- `CLAUDE.md` / `docs` — record required SNOW role + sandbox setup notes.
- `tests/test_snow_smoke.py` (new) — unit test the query construction (mock httpx).

## Implementation steps (Builder / Sonnet)

1. Add a `smoke_test` that calls `snow_client.query_records(table, "", limit=1)`
   for each table and reports reachable/row-shape.
2. Verify basic-auth and OAuth token refresh paths against sandbox creds.
3. Record the least-privilege role needed for read-only ingestion.

## Testing requirements

**Unit:** query/params construction and auth-header selection (mock httpx).
**Live validation (gated on sandbox creds):** smoke test returns 1 row per table
under both auth methods; record output or defer with "no sandbox creds".

## Acceptance criteria

- [ ] Smoke test reads 1 row from each required table (live) or deferred w/ reason.
- [ ] Both auth methods exercised.
- [ ] Least-privilege read role documented.
- [ ] Unit suite green (count recorded).

## Security-Review Criteria (Codex)

- [ ] Credentials sourced only from settings/secrets, never logged or echoed.
- [ ] Smoke test is strictly read-only (no POST/PATCH reachable from it).
- [ ] OAuth token not written to disk/logs; refresh path doesn't leak client_secret.
- [ ] Requested SNOW role is read-only and minimal (no write/admin scopes).

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

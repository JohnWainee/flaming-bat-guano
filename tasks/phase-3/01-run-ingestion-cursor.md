---
id: P3-01
title: Run ingestion vs sandbox + validate incremental cursor
phase: 3
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P3-00]
live_validation: true
---

## Context

Exercise the ingestion pipeline (SNOW → chunk → embed → Qdrant) end-to-end
against sandbox data and prove the incremental cursor in `/data/` resumes
correctly, so a re-run ingests only new/updated tickets rather than re-processing
everything.

Not an LLM surface (batch data movement) — Security-Review Criteria.

## Scope

**In:**
- Run a bounded first pass (e.g. `sysparm_limit`-capped) and record throughput,
  API call counts, and cursor file contents.
- Run a second pass; assert only new/updated records are processed.
- Verify rate-limit delay is honored so we don't hammer the sandbox.

**Out:**
- Search-quality evaluation (P3-03+).

## Files

- `services/ingestion_pipeline/main.py` — only if cursor bugs surface.
- `tests/test_ingestion.py` — add cursor-resume unit tests (mock SNOW iterator).
- `docs` — record observed throughput + tuning notes.

## Implementation steps (Builder / Sonnet)

1. Unit-test cursor read/write + resume logic with a mocked `iter_all_records`.
2. Live: run pass 1 (bounded), capture cursor + counts.
3. Live: run pass 2; confirm incremental behavior (delta only).
4. Confirm `ingestion_rate_limit_delay_seconds` is applied between pages.

## Testing requirements

**Unit:** cursor advances monotonically; resume skips already-ingested; malformed
cursor file recovers safely.
**Live (gated):** two-pass incremental proven on sandbox; record deltas.

## Acceptance criteria

- [ ] Cursor resume unit-tested (no live dep).
- [ ] Two-pass incremental verified live, or deferred w/ reason.
- [ ] Rate-limit delay honored; no sandbox throttling observed.
- [ ] Unit suite green (count recorded).

## Security-Review Criteria (Codex)

- [ ] Cursor/state files under `/data/` contain no credentials or PII beyond
      ticket sys_ids/timestamps needed to resume.
- [ ] A corrupt/attacker-modified cursor file can't cause unbounded re-pull or
      skip-all (fails safe, logs, bounded).
- [ ] Pipeline honors rate limits (no self-inflicted DoS on SNOW).

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

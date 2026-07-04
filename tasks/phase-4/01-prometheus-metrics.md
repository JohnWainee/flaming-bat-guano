---
id: P4-01
title: Prometheus metrics endpoint on the orchestrator
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P4-00]
live_validation: false
---

## Context

Expose operational metrics (request counts/latency, LLM/SNOW call outcomes,
rate-limit rejections, dead-letter depth) via a `/metrics` endpoint for
Prometheus scraping.

## Scope

**In:**
- `prometheus_client` counters/histograms for the key paths; `/metrics` endpoint.
- Instrument `/chat`, `/email`, SNOW create, LLM calls (success/failure/latency).

**Out:** Grafana dashboards (P4-02); the metrics *values* validation.

## Files

- `services/orchestrator/metrics.py` (new).
- `services/orchestrator/main.py` — add `/metrics`; wire instrumentation.
- `services/orchestrator/requirements.txt` — add `prometheus_client`.
- `tests/test_metrics.py` (new).

## Implementation steps (Builder / Sonnet)

1. Define metric objects; increment/observe at instrumentation points.
2. Add `/metrics` returning the Prometheus exposition format.
3. Unit-test that a simulated request path moves the expected counters.

## Testing requirements

**Unit:** counters/histograms update on simulated calls; `/metrics` parses.
**Live:** none.

## Acceptance criteria

- [ ] `/metrics` endpoint exposes the defined metrics.
- [ ] Key paths instrumented (requests, LLM, SNOW, rate-limit, dead-letter).
- [ ] Unit suite green (count recorded).

## Security-Review Criteria (Codex)

- [ ] `/metrics` carries no PII/high-cardinality user data in labels (no user_id,
      no ticket content as label values).
- [ ] Endpoint access is controllable (network-policy/authn note documented) —
      not an open data-leak surface.
- [ ] No secrets exposed in metric names/labels.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: n/a

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

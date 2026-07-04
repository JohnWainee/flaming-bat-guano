---
id: P4-02
title: Grafana provisioning + dashboards
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P4-01]
live_validation: true
---

## Context

Provide Grafana with a Prometheus datasource and committed dashboards for the
orchestrator's key metrics so operators have visibility from day one.

## Scope

**In:**
- Grafana provisioning config (datasource + dashboards as code).
- A starter dashboard: request rate/latency, LLM/SNOW error rates, rate-limit
  rejections, dead-letter depth.
- Compose/K8s wiring to run Grafana + Prometheus (dev).

**Out:** Alerting rules (future).

## Files

- `monitoring/grafana/` (new) — provisioning + dashboard JSON.
- `monitoring/prometheus/prometheus.yml` (new) — scrape config.
- `docker-compose.yml` / `k8s/` — add prometheus + grafana (dev/observability).

## Implementation steps (Builder / Sonnet)

1. Add Prometheus scrape config targeting the orchestrator `/metrics`.
2. Add Grafana datasource + dashboard provisioning (as code).
3. Live: bring the stack up, confirm panels populate.

## Testing requirements

**Unit:** validate dashboard/provisioning JSON/YAML parses (schema/lint).
**Live (gated):** stack up, panels render with data.

## Acceptance criteria

- [ ] Dashboards + datasource provisioned as code (no manual clickops).
- [ ] Panels cover the P4-01 metrics.
- [ ] Config lints/parses (unit); live render done or deferred w/ reason.

## Security-Review Criteria (Codex)

- [ ] Grafana default admin credentials are not hardcoded/committed; sourced from
      secrets with a change-me note.
- [ ] Prometheus/Grafana not exposed publicly by default (network policy note).
- [ ] Dashboards don't embed secrets or PII.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

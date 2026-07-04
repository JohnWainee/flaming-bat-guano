---
id: P4-04
title: Horizontal pod autoscaling config
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P4-01]
live_validation: true
---

## Context

The orchestrator (and stateless workers) should scale under load. Add HPA
manifests driven by CPU and, where sensible, the Prometheus metrics from P4-01,
with sane min/max and resource requests/limits.

## Scope

**In:**
- HPA for the orchestrator (and teams-bot/email-ingestor if beneficial).
- Ensure deployments declare resource requests/limits so HPA can function.
- Document metric source (CPU vs custom/Prometheus adapter).

**Out:** Cluster autoscaler; vertical scaling.

## Files

- `k8s/hpa-*.yaml` (new).
- `k8s/*deployment*.yaml` — add resources requests/limits if missing.
- `docs` — scaling assumptions (CPU-only servers per project constraints).

## Implementation steps (Builder / Sonnet)

1. Add resource requests/limits to target deployments.
2. Add HPA manifests (min/max/target); note custom-metric path if used.
3. Live (if cluster): generate load, observe scale-up/down.

## Testing requirements

**Unit:** manifest lint; HPA references an existing deployment + metric.
**Live (gated):** scale event observed under load.

## Acceptance criteria

- [ ] HPA manifests valid and reference real deployments/metrics.
- [ ] Deployments declare requests/limits.
- [ ] Live scale behavior observed or deferred w/ reason.
- [ ] Unit/lint green.

## Security-Review Criteria (Codex)

- [ ] Resource limits present (prevents a single pod exhausting the node — DoS
      resilience).
- [ ] Max replicas bounded (no unbounded scale that amplifies an abusive traffic
      spike into cost/quota exhaustion).
- [ ] HPA/metric source doesn't expose sensitive data.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

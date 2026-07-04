---
id: P4-08
title: Production K8s manifests — probes, limits, network policy
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P4-00, P4-03]
live_validation: true
---

## Context

Finalize the on-prem production manifests: readiness/liveness probes, resource
requests/limits, non-root/hardened pod security, and network policies restricting
traffic between services (and blocking egress except where needed).

## Scope

**In:**
- Readiness/liveness probes for each service (orchestrator `/health`, etc.).
- Resource requests/limits on all deployments.
- Pod security: non-root, read-only rootfs where feasible, drop capabilities.
- NetworkPolicies: least-privilege service-to-service + egress to SNOW/Azure only.

**Out:** HPA (P4-04, references these); secrets (P4-03).

## Files

- `k8s/*.yaml` — probes, resources, securityContext.
- `k8s/networkpolicy-*.yaml` (new).
- `docs` — production deploy checklist.

## Implementation steps (Builder / Sonnet)

1. Add probes + resources + securityContext to every deployment.
2. Author NetworkPolicies (default-deny + explicit allows).
3. Live (if cluster): apply, confirm pods healthy and policies enforced.

## Testing requirements

**Unit:** manifest lint / policy schema validation; probe endpoints exist in code.
**Live (gated):** rollout healthy; a disallowed connection is blocked.

## Acceptance criteria

- [ ] Probes + resources + hardened securityContext on all services.
- [ ] Default-deny NetworkPolicies with explicit least-privilege allows.
- [ ] Lint/validation green; live rollout done or deferred w/ reason.

## Security-Review Criteria (Codex)

- [ ] Pods run as non-root; capabilities dropped; no privileged containers.
- [ ] NetworkPolicy is default-deny; egress limited to SNOW/Azure endpoints.
- [ ] No service unintentionally exposed (dashboard/metrics/qdrant/redis internal).
- [ ] Probes don't expose sensitive info or an unauthenticated data path.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

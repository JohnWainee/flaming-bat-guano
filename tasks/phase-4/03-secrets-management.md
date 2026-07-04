---
id: P4-03
title: Secrets via K8s Secrets / Vault (remove plaintext)
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P2-00]
live_validation: true
---

## Context

Production must not carry credentials in plaintext env/manifests. Move Azure
OpenAI, ServiceNow, email/EWS, and Bot Framework secrets to K8s Secrets (with a
documented HashiCorp Vault option) and ensure the app reads them cleanly.

## Scope

**In:**
- Replace plaintext secret env in `k8s/` with `secretKeyRef` from a Secret.
- Harden/complete `k8s/secrets-template.yaml`; document Vault injection as an
  alternative.
- Confirm the app loads secrets from the mounted/injected env unchanged.

**Out:** Rotating secrets automation (future).

## Files

- `k8s/*.yaml` — deployments reference secrets via `secretKeyRef`.
- `k8s/secrets-template.yaml` — full key list, no real values.
- `docs` — K8s Secret + Vault setup instructions.

## Implementation steps (Builder / Sonnet)

1. Enumerate every secret setting from `shared/config.py`.
2. Convert deployments to `secretKeyRef`; ensure the template lists all keys.
3. Document Vault Agent/CSI injection as the alternative path.
4. Live (if cluster available): apply and confirm pods start with injected secrets.

## Testing requirements

**Unit:** a manifest lint/consistency check — every secret env in a deployment has
a matching key in `secrets-template.yaml` and vice versa.
**Live (gated):** pods start with secrets from a real Secret.

## Acceptance criteria

- [ ] No plaintext credentials in any committed manifest.
- [ ] `secrets-template.yaml` complete; keys reconcile with deployments (unit).
- [ ] Vault option documented.
- [ ] Live apply verified or deferred w/ reason.

## Security-Review Criteria (Codex)

- [ ] Grep confirms no real secret values committed anywhere (manifests, compose,
      `.env` — only `.env.example` placeholders).
- [ ] Secrets not exposed via `/metrics`, logs, or error messages.
- [ ] Template uses placeholders and a clear "replace before apply" warning.
- [ ] RBAC note: only the intended service accounts can read the Secret.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

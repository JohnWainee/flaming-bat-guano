---
id: P4-07
title: Identity verification — email From / Teams user binding
phase: 4
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: [P2-00]
live_validation: true
---

## Context

Tickets are created "for" a requester. Two spoofing risks: a forged email `From`
header creating tickets as someone else, and Teams `user_id` / `requested_for`
manipulation in group contexts. Phase 1 added a group-chat `user_id` mismatch
rejection; this task generalizes identity binding across both surfaces.

LLM-surface + identity — RT-6 is the theme.

## Scope

**In:**
- Email: verify sender identity beyond the raw `From` (e.g. authenticated
  submission mailbox, SPF/DKIM-aware handling, or an allowlist/mapping) before
  attributing a ticket; document the trust model.
- Teams: bind the conversation and any `requested_for` to the authenticated
  Bot Framework identity; reject/deny cross-user attribution.
- Consistent rejection + audit log when identity can't be verified.

**Out:** SSO/IdP integration (future).

## Files

- `services/email_ingestor/main.py` / `processing.py` — sender trust checks.
- `services/orchestrator/main.py` / `state_machine.py` — bind `requested_for`
  to authenticated identity; reject mismatches.
- `tests/redteam/test_identity_spoofing.py` (new).

## Implementation steps (Builder / Sonnet)

1. Define and document the identity trust model for each surface.
2. Enforce: email attribution only from verified senders; Teams `requested_for`
   defaults to and is validated against the authenticated user.
3. Add rejection + audit logging (PII-safe, via P4-00 logging).
4. Adversarial tests for forged From and cross-user requested_for.

## Testing requirements

**Unit/redteam:** forged `From` doesn't attribute a ticket to the spoofed user;
`requested_for` can't be set to an arbitrary other user without authorization.
**Live (gated):** exercise with real Teams/email identities; record.

## Acceptance criteria

- [ ] Identity trust model documented per surface.
- [ ] Email attribution requires a verified sender.
- [ ] Teams `requested_for` bound to authenticated identity; mismatches rejected.
- [ ] Rejections audited (PII-safe).
- [ ] Adversarial suite passes; full suite green (count recorded).

## Red-Team Checklist (Codex)

> Mode: llm-surface / identity.
- [ ] RT-6 — forged email `From` (display-name spoof, homoglyph domain) can't
      create a ticket attributed to the impersonated user.
- [ ] RT-6 — in a group chat, user A can't confirm/submit or set `requested_for`
      to user B's identity.
- [ ] RT-5 — prompt injection can't override the bound identity to redirect
      attribution.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

---
id: P2-00
title: Re-land CHG/PRB hardening + EWS onto a mergeable branch
phase: 2
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: []
live_validation: false
---

## Context

The CHG/PRB intake hardening (date normalization, human-readable confirmations,
`known_error` passthrough) and the EWS email transport were built on
`claude/funny-johnson-ktstpu` but the PR (#2) was **closed without merging**, so
none of it is in `main`. The rest of the roadmap treats this code as
**parked/assume-good** and builds on it. This task gets it back onto a reviewable,
mergeable footing so dependent tasks have a real baseline — **without** re-opening
the closed PR (per instruction, a new PR is a new change, only if the human asks).

This is an LLM-surface task because it re-lands the CONFIRM-step rendering and the
email→ticket intake path.

## Scope

**In:**
- Rebase/verify the parked commits (`1aa2341`, `a3c9a0a`, `6c92d17`) cleanly apply
  on top of the latest `main`.
- Confirm the full suite is green on the rebased state.
- Produce a clean, self-contained diff ready for human review (do **not** open a
  PR unless the human requests it).

**Out:**
- Any new feature. This is a re-land, not a rewrite.
- Teams Adaptive Cards (that's P2-01).

## Files

- No new product code expected. Touches limited to rebase conflict resolution in:
  `services/orchestrator/conversation/field_schemas.py`,
  `services/orchestrator/llm/prompts.py`,
  `services/email_ingestor/{main.py,processing.py}`,
  `shared/config.py`, `.env.example`, `CLAUDE.md`,
  `tests/{test_conversation.py,test_email_ingestor.py}`.

## Implementation steps (Builder / Sonnet)

1. `git fetch origin main` and rebase the branch onto it; resolve any conflicts,
   preferring the parked implementation where semantics are unchanged.
2. Run `pip install pydantic==2.9.2 pydantic-settings==2.5.2 pytest==8.3.3`.
3. `python -m pytest tests/ -v` — confirm 68 passing (55 conversation + ... see
   Test Evidence). If the count drifts because `main` moved, reconcile and record.
4. Skim the diff for anything that shouldn't ride along (stray files, secrets).
5. Set `status: ready_for_redteam`.

## Testing requirements

**Unit:**
- Full existing suite green post-rebase.

**Live validation (gated):**
- none (deferred: EWS/SNOW live checks belong to Phase 3 live-validation tasks).

## Acceptance criteria

- [ ] Branch rebases cleanly on latest `main` with no lost commits.
- [ ] `python -m pytest tests/` green; count recorded.
- [ ] Diff contains only the parked change (no new features, no secrets, no
      unrelated files).
- [ ] `CLAUDE.md` "Current state" reflects reality (which work is landed vs parked).
- [ ] No PR opened (human decides when to open one).

## Red-Team Checklist (Codex)

> This re-lands LLM-surface behavior; sanity-check the security-relevant bits
> survived the rebase intact rather than re-deriving them.
- [ ] RT-1 — confirm the CONFIRM step still requires explicit user confirmation
      (`_user_confirmed`) and that extracted fields can't auto-submit.
- [ ] RT-6 — confirm the group-chat `user_id` mismatch rejection (from Phase 1)
      is still present and wasn't dropped in a conflict resolution.
- [ ] RT-5 — confirm `normalize_date`/`known_error` passthrough can't smuggle
      unexpected types into the SNOW create payload.
- [ ] Diff review: no debug logging of message bodies / PII introduced.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: deferred (see above)

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

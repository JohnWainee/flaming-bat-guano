---
id: P3-06
title: Dashboard polish based on real data
phase: 3
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: [P3-03, P3-04, P3-05]
live_validation: true
---

## Context

With real data flowing, tighten the Streamlit dashboard: pagination for large
result sets, sensible empty/error states, filters (ticket type, date), and
readable rendering of search/similar/trend panels. Small, user-facing refinements
informed by how real results actually look.

LLM-surface: renders model + retrieved output to analysts.

## Scope

**In:**
- Pagination + result-count display on Semantic Search.
- Empty-state and error-state handling (no results, backend down).
- Type/date filters wired into the query.
- Consistent, escaped rendering of excerpts and trend output.

**Out:**
- New analytical features. Auth (belongs to Phase 4 hardening).

## Files

- `services/dashboard/app.py` — the above.
- `tests/test_dashboard.py` (new) — unit-test any extracted pure helpers
  (query-string building, pagination math). Streamlit UI itself validated live.

## Implementation steps (Builder / Sonnet)

1. Extract pure helpers (pagination slice, filter→query) and unit-test them.
2. Add empty/error states and pagination controls.
3. Live: click through with real data; confirm responsiveness + readability.

## Testing requirements

**Unit:** pagination + filter-query helpers.
**Live (gated):** manual walkthrough on populated instance; record.

## Acceptance criteria

- [ ] Pagination + counts on search results.
- [ ] Empty + error states handled gracefully.
- [ ] Type/date filters functional.
- [ ] Excerpts/trend output escaped (no markup injection).
- [ ] Unit suite green (count recorded).

## Red-Team Checklist (Codex)

> Mode: llm-surface.
- [ ] RT-7 — user/ticket-derived text rendered in Streamlit is escaped; no HTML/JS
      injection via a crafted ticket excerpt.
- [ ] RT-4 — filters can't be manipulated to surface records outside intended scope.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

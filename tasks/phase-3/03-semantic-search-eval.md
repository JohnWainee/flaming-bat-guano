---
id: P3-03
title: Semantic-search quality eval harness (golden queries, precision@k)
phase: 3
status: todo
builder: sonnet
redteam_by: codex
redteam: llm-surface
depends_on: [P3-02]
live_validation: true
---

## Context

Prove semantic search is actually useful on real ticket data: build a repeatable
eval harness with a labeled set of golden queries and measure precision@k /
recall so we can catch regressions in embeddings, chunking, or search params.

LLM-surface: embeddings + retrieval feed analyst-facing results and, downstream,
similar-ticket suggestions to end users.

## Scope

**In:**
- A golden set (`tests/eval/search_golden.jsonl`): query → known-relevant
  ticket sys_ids.
- An eval runner computing precision@k, recall@k, MRR over the set.
- A documented quality baseline + threshold below which the harness fails.

**Out:**
- Similar-ticket UX (P3-04); trend analysis (P3-05).

## Files

- `tests/eval/search_golden.jsonl` (new).
- `services/orchestrator/vector/eval.py` (new) — metric computation (pure).
- `tests/test_search_eval.py` (new) — unit-test metric math on synthetic rankings.
- `docs` — baseline numbers.

## Implementation steps (Builder / Sonnet)

1. Implement precision@k/recall@k/MRR as pure functions; unit-test on synthetic
   rankings (no live dep).
2. Curate ~20–30 golden queries from sandbox tickets with labeled relevants.
3. Live: run the harness, record baseline, set a regression threshold.

## Testing requirements

**Unit:** metric functions correct on hand-computed cases.
**Live (gated):** harness runs against populated Qdrant; baseline recorded.

## Acceptance criteria

- [ ] Metric functions pure + unit-tested.
- [ ] Golden set committed; harness runnable with one command.
- [ ] Baseline + threshold documented (or live run deferred w/ reason).
- [ ] Unit suite green (count recorded).

## Red-Team Checklist (Codex)

> Mode: llm-surface. Add cases under `tests/redteam/test_search_injection.py`.
- [ ] RT-2 — a ticket whose body contains injection text ("ignore previous…",
      fake system instructions) is treated as **data**: it can appear in results
      but cannot alter ranking logic or downstream prompt behavior.
- [ ] RT-3 — search cannot be steered to exfiltrate tickets a given surface
      shouldn't return (scope/filter respected).
- [ ] RT-4 — result excerpts don't leak PII fields the dashboard shouldn't show.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

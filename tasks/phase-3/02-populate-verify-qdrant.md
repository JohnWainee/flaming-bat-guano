---
id: P3-02
title: Populate Qdrant collections + verify embeddings and counts
phase: 3
status: todo
builder: sonnet
redteam_by: codex
redteam: security-review
depends_on: [P3-01]
live_validation: true
---

## Context

After ingestion, confirm the Qdrant collections exist with the right vector
dimensionality, that point counts reconcile against tickets ingested, and that a
spot-check embedding round-trips (upsert → search returns the same point).

Not an LLM surface in the adversarial sense — Security-Review Criteria.

## Scope

**In:**
- Verify collection config (distance metric, `azure_openai_embedding_dimensions`).
- Reconcile Qdrant point count vs chunks produced by ingestion.
- Spot-check: embed a known ticket, search, confirm self-retrieval at top-1.

**Out:**
- Relevance/precision evaluation (P3-03).

## Files

- `services/orchestrator/vector/client.py` — only if config mismatches surface.
- `tests/test_vector_client.py` (new) — unit-test collection ensure + payload shape (mock Qdrant).
- `docs` — record counts + config snapshot.

## Implementation steps (Builder / Sonnet)

1. Unit-test `ensure_collections` params and `upsert_chunks_batch` payload shape.
2. Live: assert collection vector size == configured dims.
3. Live: reconcile counts (tolerance for chunking fan-out documented).
4. Live: self-retrieval spot check.

## Testing requirements

**Unit:** collection ensure uses configured dims/metric; upsert payload carries
ticket metadata needed for `SearchResult`.
**Live (gated):** dims match, counts reconcile, self-retrieval top-1.

## Acceptance criteria

- [ ] Collection dims/metric verified against config.
- [ ] Point count reconciles with ingested chunks (within documented tolerance).
- [ ] Self-retrieval spot check passes (or deferred w/ reason).
- [ ] Unit suite green (count recorded).

## Security-Review Criteria (Codex)

- [ ] Qdrant not exposed without the configured API key; no anonymous write path.
- [ ] Stored payloads contain only fields needed for search/display — no excess
      PII beyond what the dashboard requires.
- [ ] Embedding calls to Azure OpenAI don't log raw ticket text at INFO.

## Test Evidence (Builder fills)

- Suite: `<N> passed` on commit `<sha>`
- Live validation: <done + evidence | deferred: reason>

## Red-Team Findings (Codex fills)

- <none yet>

## Handoff Log

- 2026-07-04 — planning — task created (status: todo).

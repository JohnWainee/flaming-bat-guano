# ServiceNow LLM Assistant — Project Context

## What this project is

A two-part solution to ServiceNow pain points for an organization with ~500–5k users and 50k–500k historical tickets:

1. **Chatbot intake** — Conversational LLM front-end (Teams + email) that guides users through creating INC/REQ/CHG/PRB tickets and submits them via ServiceNow Table REST API.
2. **Analyst dashboard** — Streamlit UI backed by a Qdrant vector store of all historical tickets, with semantic search, similar-ticket finder, and LLM-generated trend analysis.

## Key architectural decisions (locked in)

| Concern | Decision | Why |
|---|---|---|
| LLM | Azure OpenAI GPT-4o-mini + text-embedding-3-small | High data sensitivity; tenant-isolated; customer already has Azure |
| Vector DB | Qdrant (self-hosted on-prem) | Rust-based, Docker-native, stays on-prem |
| Chatbot surface | Microsoft Teams + email (IMAP/EWS) | Where users currently work |
| Infrastructure | Docker Compose (dev) + Kubernetes (prod, on-prem) | Customer has Docker/K8s; CPU-only servers |
| Language | Python 3.12 | Best LLM/ML ecosystem |
| SNOW auth | Basic auth (default) or OAuth 2.0 | API access only, no admin UI |

## Current state: Phase 1 MERGED ✅

**Branch:** `main` (PR #1 merged)  
**All 37 unit tests passing.**

### What was built

```
services/
  orchestrator/          # FastAPI core — POST /chat, POST /email, GET /health
    llm/client.py        # Azure OpenAI async wrapper (chat_complete, embed, embed_single)
    llm/prompts.py       # System prompt, classify prompt, field question/confirm formatters
    snow/client.py       # ServiceNow Table API (create, get, update, iter_all_records)
    vector/client.py     # Qdrant async client (ensure_collections, upsert_chunks_batch, search_similar)
    conversation/
      state_machine.py   # GREETING→CLASSIFY→COLLECT→CONFIRM→SUBMITTED; all LLM calls lazy-imported
      field_schemas.py   # Required fields per ticket type + normalize_field()
    state_store.py       # Redis-backed ConversationState persistence (TTL: 1hr)
    main.py              # FastAPI app + lifespan (ensures Qdrant collections on startup)
  teams_bot/main.py      # aiohttp + Bot Framework adapter → POST /chat
  email_ingestor/main.py # IMAP polling, parseaddr(), sync HTTP, run_in_executor
  ingestion_pipeline/main.py  # SNOW→chunk→embed→Qdrant with incremental cursor in /data/
  dashboard/app.py       # Streamlit: Semantic Search, Similar Tickets, Trend Analysis
shared/
  models.py              # Pydantic: TicketType, ConversationState, SearchResult, etc.
  config.py              # pydantic-settings from .env
docker-compose.yml       # qdrant, redis, orchestrator, teams-bot, email-ingestor, ingestion-pipeline, dashboard
k8s/                     # Deployments, PVCs, CronJob, secrets-template.yaml
tests/
  test_conversation.py   # 30 tests: normalization, intent detection, state machine, prompts
  test_ingestion.py      # 7 tests: chunking, record-to-text
```

### Bugs fixed before merge (Copilot review)
- Teams bot: async no-op handler + async /health handler
- Orchestrator: reject state when user_id mismatches (group chat isolation)
- Email ingestor: `parseaddr()` for From header; sync HTTP client; `run_in_executor` for blocking IMAP
- State machine: word-boundary `_user_cancelled` (was matching "not working"); removed cancel branch in CONFIRM so corrections are in-place
- Dashboard: removed unused imports
- docker-compose: added missing `ingestion-pipeline` service

## Phases remaining

### Phase 2 — Email hardening + CHG/PRB intake (2–3 weeks)
- EWS support option in email ingestor (currently IMAP only; `exchangelib` is in requirements)
- Extend conversation flow for `change_request` and `problem` required fields (already in `field_schemas.py`)
- Teams Adaptive Cards for the CONFIRM step (rich structured card with Edit/Confirm buttons)
- Cards directory: `services/teams_bot/cards/` (empty)

### Phase 3 — Historical ingestion + dashboard validation (3–4 weeks)
- Run ingestion pipeline against real/sandbox SNOW instance
- Populate Qdrant collections, validate semantic search quality
- Dashboard polish based on real data

### Phase 4 — Hardening + production K8s (2 weeks)
- Rate limiting + retry/dead-letter in orchestrator
- Prometheus metrics endpoint on FastAPI + Grafana
- Secrets via K8s Secrets or HashiCorp Vault
- Horizontal pod autoscaling config

## How to run locally

```bash
cp .env.example .env
# Fill in Azure OpenAI, ServiceNow, email, and Bot Framework credentials

docker-compose up            # starts everything except ingestion-pipeline
docker-compose run ingestion-pipeline   # one-shot historical load
# Orchestrator:  http://localhost:8000
# Teams bot:     http://localhost:3978
# Dashboard:     http://localhost:8501
```

## Running tests

```bash
pip install pydantic==2.9.2 pydantic-settings==2.5.2 pytest==8.3.3
python -m pytest tests/ -v
```

## ServiceNow API access needed

Tables: `incident`, `sc_request`, `sc_req_item`, `change_request`, `problem`

Endpoints:
- `GET  /api/now/table/{table}` — query (supports `sysparm_query`, `sysparm_fields`, `sysparm_limit`, `sysparm_offset`)
- `POST /api/now/table/{table}` — create
- `PATCH /api/now/table/{table}/{sys_id}` — update (work notes)

## Environment variables (see .env.example for full list)

Critical ones to set first:
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`
- `SNOW_INSTANCE_URL`, `SNOW_USERNAME`, `SNOW_PASSWORD`
- `MICROSOFT_APP_ID`, `MICROSOFT_APP_PASSWORD` (from Azure Bot Service registration)
- `EMAIL_HOST`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`

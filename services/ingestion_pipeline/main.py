from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from shared.config import settings
from shared.models import TicketChunk, TicketType

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

_CURSOR_FILE = Path("/data/ingestion_cursor.txt")

_TABLE_MAP: Dict[TicketType, str] = {
    TicketType.INCIDENT: "incident",
    TicketType.REQUEST: "sc_request",
    TicketType.CHANGE: "change_request",
    TicketType.PROBLEM: "problem",
}

_FIELDS: Dict[TicketType, List[str]] = {
    TicketType.INCIDENT: [
        "number", "sys_id", "short_description", "description",
        "work_notes", "close_notes", "category", "urgency", "impact",
        "state", "assigned_to", "resolved_at", "sys_updated_on",
    ],
    TicketType.REQUEST: [
        "number", "sys_id", "short_description", "description",
        "special_instructions", "state", "requested_for", "sys_updated_on",
    ],
    TicketType.CHANGE: [
        "number", "sys_id", "short_description", "description",
        "implementation_plan", "backout_plan", "test_plan",
        "risk", "impact", "type", "state", "sys_updated_on",
    ],
    TicketType.PROBLEM: [
        "number", "sys_id", "short_description", "description",
        "work_notes", "known_error", "resolution_code", "sys_updated_on",
    ],
}

_CHUNK_TOKENS = 400  # approximate tokens per chunk (chars / 4)
_EMBED_BATCH = 32


def _load_cursor() -> Optional[str]:
    if _CURSOR_FILE.exists():
        return _CURSOR_FILE.read_text().strip() or None
    return None


def _save_cursor(ts: str) -> None:
    _CURSOR_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CURSOR_FILE.write_text(ts)


def _record_to_text(record: Dict[str, Any], ticket_type: TicketType) -> str:
    parts = []
    if sd := record.get("short_description"):
        parts.append(f"Summary: {sd}")
    if desc := record.get("description"):
        parts.append(f"Description: {desc}")
    for extra in ("work_notes", "close_notes", "resolution_code", "implementation_plan", "backout_plan", "test_plan", "special_instructions"):
        if val := record.get(extra):
            parts.append(f"{extra.replace('_', ' ').title()}: {val}")
    return "\n\n".join(p for p in parts if p.strip())


def _chunk_text(text: str, max_chars: int = _CHUNK_TOKENS * 4) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    while text:
        chunk = text[:max_chars]
        last_newline = chunk.rfind("\n")
        if last_newline > max_chars // 2:
            chunk = chunk[:last_newline]
        chunks.append(chunk.strip())
        text = text[len(chunk):].strip()
    return chunks


async def ingest_table(ticket_type: TicketType, since: Optional[str]) -> int:
    from services.orchestrator.llm.client import embed
    from services.orchestrator.snow.client import snow_client
    from services.orchestrator.vector.client import vector_client

    table = _TABLE_MAP[ticket_type]
    fields = _FIELDS[ticket_type]
    query = f"sys_updated_on>={since}" if since else "active=false^ORactive=true"

    logger.info("Ingesting %s from table %s (since=%s)", ticket_type.value, table, since)

    chunk_buffer: List[TicketChunk] = []
    embed_buffer: List[str] = []
    total = 0

    async for record in snow_client.iter_all_records(
        table, query, fields=fields,
        page_size=settings.ingestion_batch_size,
        rate_limit_delay=settings.ingestion_rate_limit_delay_seconds,
    ):
        text = _record_to_text(record, ticket_type)
        if not text.strip():
            continue

        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            tc = TicketChunk(
                ticket_number=record.get("number", ""),
                sys_id=record.get("sys_id", ""),
                ticket_type=ticket_type,
                chunk_index=i,
                text=chunk,
                metadata={
                    "state": record.get("state", ""),
                    "sys_updated_on": record.get("sys_updated_on", ""),
                    "category": record.get("category", ""),
                },
            )
            chunk_buffer.append(tc)
            embed_buffer.append(chunk)

        if len(embed_buffer) >= _EMBED_BATCH:
            embeddings = await embed(embed_buffer)
            await vector_client.upsert_chunks_batch(chunk_buffer, embeddings)
            total += len(chunk_buffer)
            logger.info("Upserted %d chunks for %s (running total: %d)", len(chunk_buffer), ticket_type.value, total)
            chunk_buffer.clear()
            embed_buffer.clear()

    if embed_buffer:
        embeddings = await embed(embed_buffer)
        await vector_client.upsert_chunks_batch(chunk_buffer, embeddings)
        total += len(chunk_buffer)

    logger.info("Finished ingesting %s: %d total chunks", ticket_type.value, total)
    return total


async def run_ingestion() -> None:
    from services.orchestrator.vector.client import vector_client

    await vector_client.ensure_collections()

    since = _load_cursor()
    run_start = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for ticket_type in TicketType:
        try:
            await ingest_table(ticket_type, since)
        except Exception as exc:
            logger.error("Ingestion failed for %s: %s", ticket_type.value, exc, exc_info=True)

    _save_cursor(run_start)
    logger.info("Ingestion complete. Cursor saved: %s", run_start)


if __name__ == "__main__":
    asyncio.run(run_ingestion())

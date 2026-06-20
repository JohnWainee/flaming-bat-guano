from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from shared.config import settings
from shared.models import SearchResult, TicketChunk, TicketType

_COLLECTIONS = {
    TicketType.INCIDENT: "incidents",
    TicketType.REQUEST: "requests",
    TicketType.CHANGE: "changes",
    TicketType.PROBLEM: "problems",
}
_ALL_COLLECTIONS = list(_COLLECTIONS.values())

_client: Optional[AsyncQdrantClient] = None


def _get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
    return _client


class VectorClient:
    async def ensure_collections(self) -> None:
        client = _get_client()
        existing = {c.name for c in await client.get_collections().collections}
        for name in _ALL_COLLECTIONS:
            if name not in existing:
                await client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=settings.azure_openai_embedding_dimensions,
                        distance=Distance.COSINE,
                    ),
                )

    async def upsert_chunk(self, chunk: TicketChunk, embedding: List[float]) -> None:
        client = _get_client()
        collection = _COLLECTIONS[chunk.ticket_type]
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.sys_id}:{chunk.chunk_index}"))
        payload: Dict[str, Any] = {
            "ticket_number": chunk.ticket_number,
            "sys_id": chunk.sys_id,
            "ticket_type": chunk.ticket_type.value,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            **chunk.metadata,
        }
        await client.upsert(
            collection_name=collection,
            points=[PointStruct(id=point_id, vector=embedding, payload=payload)],
        )

    async def upsert_chunks_batch(
        self, chunks: List[TicketChunk], embeddings: List[List[float]]
    ) -> None:
        client = _get_client()
        by_collection: Dict[str, list] = {name: [] for name in _ALL_COLLECTIONS}
        for chunk, embedding in zip(chunks, embeddings):
            collection = _COLLECTIONS[chunk.ticket_type]
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{chunk.sys_id}:{chunk.chunk_index}"))
            payload: Dict[str, Any] = {
                "ticket_number": chunk.ticket_number,
                "sys_id": chunk.sys_id,
                "ticket_type": chunk.ticket_type.value,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                **chunk.metadata,
            }
            by_collection[collection].append(PointStruct(id=point_id, vector=embedding, payload=payload))
        for collection, points in by_collection.items():
            if points:
                await client.upsert(collection_name=collection, points=points)

    async def search_similar(
        self,
        query: str,
        ticket_types: Optional[List[TicketType]] = None,
        limit: int = 5,
    ) -> List[SearchResult]:
        from services.orchestrator.llm.client import embed_single

        embedding = await embed_single(query)
        target_types = ticket_types or list(TicketType)
        all_results: List[SearchResult] = []

        client = _get_client()
        for ticket_type in target_types:
            collection = _COLLECTIONS[ticket_type]
            hits = await client.search(
                collection_name=collection,
                query_vector=embedding,
                limit=limit,
            )
            for hit in hits:
                payload = hit.payload or {}
                all_results.append(SearchResult(
                    ticket_number=payload.get("ticket_number", ""),
                    sys_id=payload.get("sys_id", ""),
                    ticket_type=ticket_type,
                    score=hit.score,
                    excerpt=payload.get("text", "")[:300],
                    metadata={k: v for k, v in payload.items() if k not in {"text", "ticket_number", "sys_id", "ticket_type", "chunk_index"}},
                ))

        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:limit]

    async def search_collection(
        self,
        query_embedding: List[float],
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> list:
        client = _get_client()
        query_filter = None
        if filters:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filters.items()
            ]
            query_filter = Filter(must=conditions)
        return await client.search(
            collection_name=collection,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
        )


vector_client = VectorClient()

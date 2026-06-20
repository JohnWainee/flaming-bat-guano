from __future__ import annotations

import json
from typing import Optional

import redis.asyncio as aioredis

from shared.config import settings
from shared.models import ConversationState

_pool: Optional[aioredis.ConnectionPool] = None


def _get_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)
    return _pool


def _key(conversation_id: str) -> str:
    return f"conv:{conversation_id}"


async def load_state(conversation_id: str) -> Optional[ConversationState]:
    client = aioredis.Redis(connection_pool=_get_pool())
    data = await client.get(_key(conversation_id))
    if data is None:
        return None
    return ConversationState.model_validate_json(data)


async def save_state(state: ConversationState) -> None:
    client = aioredis.Redis(connection_pool=_get_pool())
    await client.setex(
        _key(state.conversation_id),
        settings.conversation_ttl_seconds,
        state.model_dump_json(),
    )


async def delete_state(conversation_id: str) -> None:
    client = aioredis.Redis(connection_pool=_get_pool())
    await client.delete(_key(conversation_id))

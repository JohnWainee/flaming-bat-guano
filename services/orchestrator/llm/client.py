from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import AsyncAzureOpenAI

from shared.config import settings

_client: Optional[AsyncAzureOpenAI] = None


def get_client() -> AsyncAzureOpenAI:
    global _client
    if _client is None:
        _client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
    return _client


async def chat_complete(
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> Any:
    kwargs: Dict[str, Any] = {
        "model": settings.azure_openai_chat_deployment,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice or "auto"
    response = await get_client().chat.completions.create(**kwargs)
    return response.choices[0].message


async def embed(texts: List[str]) -> List[List[float]]:
    response = await get_client().embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=texts,
        dimensions=settings.azure_openai_embedding_dimensions,
    )
    return [item.embedding for item in response.data]


async def embed_single(text: str) -> List[float]:
    results = await embed([text])
    return results[0]

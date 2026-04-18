"""Chat service — wraps RAG pipeline with caching and session management."""
from __future__ import annotations
import json
import logging
from app.rag.pipeline import RAGPipeline
from app.models.schemas import ChatQueryRequest, ChatQueryResponse

logger = logging.getLogger(__name__)
_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


async def process_query(request: ChatQueryRequest) -> ChatQueryResponse:
    """Process a chat query through the RAG pipeline with Redis caching."""
    pipeline = get_pipeline()

    # Try cache for identical recent queries (saves cost on repeat questions)
    cache_key = f"query:{request.stream_type.value}:{hash(request.query)}"
    cached = await _get_cache(cache_key)
    if cached:
        logger.info(f"Cache hit for query hash {hash(request.query)}")
        return ChatQueryResponse(**cached)

    response = await pipeline.query(request)

    # Cache for 1 hour — do not cache knowledge gaps
    if not response.is_knowledge_gap:
        await _set_cache(cache_key, response.model_dump(mode="json"))

    return response


async def _get_cache(key: str) -> dict | None:
    try:
        import redis.asyncio as aioredis
        from app.core.config import settings
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        val = await r.get(key)
        await r.aclose()
        return json.loads(val) if val else None
    except Exception:
        return None


async def _set_cache(key: str, value: dict, ttl: int = 3600):
    try:
        import redis.asyncio as aioredis
        from app.core.config import settings
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.setex(key, ttl, json.dumps(value, default=str))
        await r.aclose()
    except Exception:
        pass  # Cache failure is non-fatal

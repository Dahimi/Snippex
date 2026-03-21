import hashlib
import logging
from typing import Optional

from models.request import SearchRequest
from models.response import SearchResponse

logger = logging.getLogger(__name__)

# TTL in seconds by search depth
_TTL: dict[str, int] = {
    "precise": 43200,     # 12h — fewer results, stable
    "balanced": 14400,    #  4h — default
    "exhaustive": 28800,  #  8h — expensive to recompute
}

_client = None


def _get_client():
    """Lazily initialise the Upstash Redis client. Returns None if not configured."""
    global _client
    if _client is not None:
        return _client
    try:
        from config import settings
        if not settings.UPSTASH_REDIS_URL or not settings.UPSTASH_REDIS_TOKEN:
            return None
        from upstash_redis.asyncio import Redis
        _client = Redis(
            url=settings.UPSTASH_REDIS_URL,
            token=settings.UPSTASH_REDIS_TOKEN,
        )
        logger.info("Upstash Redis cache initialised.")
    except Exception as exc:
        logger.warning("Redis cache unavailable: %s", exc)
    return _client


def _cache_key(request: SearchRequest) -> str:
    """Deterministic cache key from all request fields that affect output."""
    parts = "|".join([
        request.query.lower().strip(),
        request.search_depth,
        str(request.num_results),
        str(request.max_snippets_per_result),
        request.recency or "",
        request.language or "en",
        ",".join(sorted(request.include_domains or [])),
        ",".join(sorted(request.exclude_domains or [])),
    ])
    digest = hashlib.sha256(parts.encode()).hexdigest()
    return f"snx:search:{digest}"


async def get_cached(request: SearchRequest) -> Optional[SearchResponse]:
    """Return a cached SearchResponse, or None on miss / unavailability."""
    client = _get_client()
    if client is None:
        return None
    try:
        data = await client.get(_cache_key(request))
        if data:
            logger.debug("Cache HIT for query=%r", request.query)
            return SearchResponse.model_validate_json(data)
        logger.debug("Cache MISS for query=%r", request.query)
    except Exception as exc:
        logger.warning("Cache get error (continuing without cache): %s", exc)
    return None


async def set_cached(request: SearchRequest, response: SearchResponse) -> None:
    """Store a SearchResponse in the cache. Silently skips on error."""
    client = _get_client()
    if client is None:
        return
    try:
        ttl = _TTL.get(request.search_depth, 14400)
        await client.set(_cache_key(request), response.model_dump_json(), ex=ttl)
        logger.debug("Cache SET for query=%r (ttl=%ds)", request.query, ttl)
    except Exception as exc:
        logger.warning("Cache set error (continuing without cache): %s", exc)

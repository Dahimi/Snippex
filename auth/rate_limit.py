"""
Per-API-key rate limiting using Upstash Redis.
Uses a fixed window (1 hour) counter per key.

Limits (configurable in config.py):
  - admin keys  → unlimited
  - user keys   → RATE_LIMIT_USER_PER_HOUR requests/hour
  - internal    → unlimited (playground proxy has its own limit on the frontend)

Silently skips enforcement if Redis is not configured.
"""

import hashlib
import logging
from fastapi import HTTPException
from auth.api_key import UserContext
from config import settings

logger = logging.getLogger(__name__)

_WINDOW_SECONDS = 3600  # 1 hour

_redis_client = None


def _redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        from upstash_redis.asyncio import Redis
        if not settings.UPSTASH_REDIS_URL or not settings.UPSTASH_REDIS_TOKEN:
            return None
        _redis_client = Redis(url=settings.UPSTASH_REDIS_URL, token=settings.UPSTASH_REDIS_TOKEN)
    except Exception as exc:
        logger.warning("Rate limit Redis unavailable: %s", exc)
    return _redis_client


def _rate_limit_for(ctx: UserContext) -> int:
    """Return requests-per-hour limit. 0 = unlimited."""
    if ctx.is_admin or ctx.is_internal:
        return 0
    return settings.RATE_LIMIT_USER_PER_HOUR


async def check_rate_limit(ctx: UserContext, raw_key: str) -> None:
    """
    Enforce the rate limit for this UserContext.
    Raises HTTP 429 if the limit is exceeded.
    Skips silently if Redis is unavailable.
    """
    limit = _rate_limit_for(ctx)
    if limit == 0:
        return  # unlimited

    redis = _redis()
    if redis is None:
        return  # Redis not configured — skip enforcement

    # Hash the raw API key so we never store it in Redis
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()[:16]
    redis_key = f"snx:ratelimit:{key_hash}"

    try:
        count = await redis.incr(redis_key)
        if count == 1:
            # First request in window — set expiry
            await redis.expire(redis_key, _WINDOW_SECONDS)

        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {limit} requests/hour. Upgrade your plan for higher limits.",
                headers={"X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0"},
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Rate limit check failed (skipping): %s", exc)

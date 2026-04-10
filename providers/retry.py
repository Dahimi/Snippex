"""
Shared retry utility for provider API calls.
Usage:
    result = await with_retry(lambda: client.post(...), label="perplexity")
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def with_retry(coro_fn, retries: int = 1, delay: float = 0.5, label: str = ""):
    """
    Calls coro_fn() up to retries+1 times on transient failures.
    Re-raises the last exception if all attempts fail.
    """
    for attempt in range(retries + 1):
        try:
            return await coro_fn()
        except Exception as exc:
            if attempt < retries:
                logger.warning(
                    "%s transient error (attempt %d/%d): %s — retrying in %.1fs",
                    label, attempt + 1, retries + 1, exc, delay,
                )
                await asyncio.sleep(delay)
            else:
                raise

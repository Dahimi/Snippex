import time
from fastapi import HTTPException
from supabase import create_client, Client
from config import settings

_supabase: Client | None = None

# Per-user balance cache — avoids a Supabase round-trip on most requests.
# TTL of 30s bounds how stale the cached balance can be.
_BALANCE_CACHE_TTL = 30
_balance_cache: dict[str, tuple[int, float]] = {}  # user_id -> (balance, expiry)


def _db() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase


def check_and_reserve_credit(user_id: str) -> bool:
    """
    Ensures the user has credits before processing a request.

    Fast path (cache hit, balance > 0): decrements the local cache and returns
    True — the caller must queue deduct_credit_background() as a background task.

    Slow path (cache miss or balance at zero): calls Supabase synchronously,
    raises HTTP 402 if no credits remain, caches the new balance, returns False.

    Safe under asyncio's single-threaded event loop — no await points means the
    cache read-modify-write is atomic from the perspective of concurrent coroutines.
    """
    cached = _balance_cache.get(user_id)
    now = time.monotonic()

    if cached is not None:
        balance, expiry = cached
        if now < expiry:
            if balance > 0:
                # Fast path — skip Supabase, queue deduction in background
                _balance_cache[user_id] = (balance - 1, expiry)
                return True
            # Cached balance is zero — fall through to re-check in case user topped up
            # (intentionally not returning 402 here; the DB is the source of truth)

    # Slow path — hit Supabase
    result = _db().rpc("consume_credit", {"p_user_id": user_id}).execute()
    remaining = result.data

    if remaining == -1:
        raise HTTPException(
            status_code=402,
            detail="No credits remaining. Top up your account to continue.",
        )

    _balance_cache[user_id] = (remaining, now + _BALANCE_CACHE_TTL)
    return False  # already deducted synchronously


def deduct_credit_background(user_id: str) -> None:
    """
    Background deduction — called after the response is sent.
    Best-effort: never raises. Updates the balance cache with the fresh DB value.
    """
    try:
        result = _db().rpc("consume_credit", {"p_user_id": user_id}).execute()
        remaining = result.data
        if remaining != -1:
            _balance_cache[user_id] = (remaining, time.monotonic() + _BALANCE_CACHE_TTL)
    except Exception:
        pass


def increment_usage(user_id: str) -> None:
    """Record one request in the usage table (best-effort, never raises)."""
    try:
        from datetime import date
        _db().rpc(
            "increment_usage",
            {"p_user_id": user_id, "p_date": date.today().isoformat()},
        ).execute()
    except Exception:
        pass

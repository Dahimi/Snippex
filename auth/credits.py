from fastapi import HTTPException
from supabase import create_client, Client
from config import settings

_supabase: Client | None = None


def _db() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase


def consume_credit(user_id: str) -> int:
    """
    Atomically decrement credits by 1 using the consume_credit Postgres function.
    Returns the new remaining balance.
    Raises HTTP 402 if the user has no credits left.
    """
    result = _db().rpc("consume_credit", {"p_user_id": user_id}).execute()
    remaining = result.data

    if remaining == -1:
        raise HTTPException(
            status_code=402,
            detail="No credits remaining. Top up your account to continue.",
        )

    return remaining


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

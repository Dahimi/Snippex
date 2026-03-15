from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config import settings

_bearer = HTTPBearer()

def _get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> str:
    """
    Validates a Bearer API key. Accepts two forms:
    - Internal service key (INTERNAL_SERVICE_KEY): used by the web app's playground proxy.
    - User API key (snx_...): validated against the Supabase api_keys table.
    Returns the owner's user_id (or "internal") on success, raises 401 otherwise.
    """
    key = credentials.credentials

    if key == settings.INTERNAL_SERVICE_KEY:
        return "internal"

    if not key.startswith("snx_"):
        raise HTTPException(status_code=401, detail="Invalid API key format.")

    db = _get_supabase()
    result = (
        db.table("api_keys")
        .select("user_id")
        .eq("key", key)
        .maybe_single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key.")

    return result.data["user_id"]

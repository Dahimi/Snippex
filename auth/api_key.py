from dataclasses import dataclass
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config import settings

_bearer = HTTPBearer()


@dataclass
class UserContext:
    user_id: str
    role: str  # "user" | "admin"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_internal(self) -> bool:
        return self.user_id == "internal"


def _get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> UserContext:
    """
    Validates a Bearer API key. Returns a UserContext on success, raises 401 otherwise.

    - INTERNAL_SERVICE_KEY  → UserContext("internal", "admin")  [playground proxy]
    - snx_... user key      → UserContext(user_id, role) from Supabase
    """
    key = credentials.credentials

    if key == settings.INTERNAL_SERVICE_KEY:
        return UserContext(user_id="internal", role="admin")

    if not key.startswith("snx_"):
        raise HTTPException(status_code=401, detail="Invalid API key format.")

    db = _get_supabase()
    result = (
        db.table("api_keys")
        .select("user_id, role")
        .eq("key", key)
        .maybe_single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key.")

    return UserContext(
        user_id=result.data["user_id"],
        role=result.data.get("role", "user"),
    )

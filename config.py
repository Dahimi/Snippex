from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Search Provider: Perplexity
    PERPLEXITY_API_KEY: str
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai"
    
    # LLM Provider: Cerebras
    CEREBRAS_API_KEY: str
    CEREBRAS_BASE_URL: str = "https://api.cerebras.ai/v1"
    CEREBRAS_MODEL: str = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")
    
    # Supabase (for API key validation)
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Internal service key — used by the web app's playground proxy
    INTERNAL_SERVICE_KEY: str

    # Upstash Redis — optional, cache is disabled if not set
    UPSTASH_REDIS_URL: Optional[str] = None
    UPSTASH_REDIS_TOKEN: Optional[str] = None

    # GCS telemetry — optional, falls back to local JSONL if not set
    GCS_LOG_BUCKET: Optional[str] = None

    # Stripe billing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_SUCCESS_URL: str = "https://snippex.ai/billing/success"
    STRIPE_CANCEL_URL: str = "https://snippex.ai/billing/cancel"

    # Project Settings
    DEFAULT_NUM_RESULTS: int = 5
    MAX_NUM_RESULTS: int = 10
    DEFAULT_MAX_SNIPPETS_PER_RESULT: int = 3
    RATE_LIMIT_USER_PER_HOUR: int = os.getenv("RATE_LIMIT_USER_PER_HOUR", 100)  # 0 = unlimited
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

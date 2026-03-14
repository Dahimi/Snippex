from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Search Provider: Perplexity
    PERPLEXITY_API_KEY: str
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai"
    
    # LLM Provider: Cerebras
    CEREBRAS_API_KEY: str
    CEREBRAS_BASE_URL: str = "https://api.cerebras.ai/v1"
    CEREBRAS_MODEL: str = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")
    
    # Project Settings
    DEFAULT_NUM_RESULTS: int = 5
    MAX_NUM_RESULTS: int = 10
    DEFAULT_MAX_SNIPPETS_PER_RESULT: int = 3
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

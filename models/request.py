from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str
    num_results: int = Field(default=5, ge=1, le=10)
    max_snippets_per_result: int = Field(default=3, ge=1, le=5)
    recency: Optional[str] = None  # "day", "week", "month", "year"
    language: Optional[str] = "en"
    include_domains: List[str] = Field(default_factory=list)
    exclude_domains: List[str] = Field(default_factory=list)
    search_depth: str = "balanced"  # "precise" | "balanced" | "exhaustive"
    debug: bool = False

from pydantic import BaseModel, Field
from typing import List, Optional

# --- LLM output (internal, never exposed to API user) ---

class SnippetAnchor(BaseModel):
    """
    Anchor pair returned by the LLM.
    head: exact first 3-5 words of the target passage (verbatim from source)
    tail: exact last 3-5 words of the target passage (verbatim from source)
    relevance_score: LLM-estimated relevance to the query (0.0–1.0)
    """
    head: str
    tail: str
    relevance_score: float

class AnchorExtractionResult(BaseModel):
    anchors: List[SnippetAnchor]

# --- Public API response models ---

class Snippet(BaseModel):
    model_config = {"populate_by_name": True}

    text: str                  # reconstructed from anchor + source content
    relevance_score: float     # 0.0–1.0, passed through from LLM anchor
    head: Optional[str] = Field(default=None, exclude=True)
    tail: Optional[str] = Field(default=None, exclude=True)

class SearchResult(BaseModel):
    rank: int
    url: str
    title: str
    snippets: List[Snippet]    # our reconstructed relevant passages
    publish_date: Optional[str] = None
    last_updated: Optional[str] = None

    # Internal fields — never serialised in API responses
    warning: Optional[str] = Field(default=None, exclude=True)
    search_snippet: Optional[str] = Field(default=None, exclude=True)
    original_content: Optional[str] = Field(default=None, exclude=True)

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_latency_ms: int

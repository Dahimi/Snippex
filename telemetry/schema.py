"""
Pydantic models for the per-request telemetry log entry.

One JSON file is written to GCS per search request, partitioned by date:
  gs://<bucket>/requests/YYYY/MM/DD/<request_id>.json
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AnchorLog(BaseModel):
    """Raw anchor pair as returned by the LLM, before reconstruction."""
    head: str
    tail: str
    relevance_score: float


class ReconstructionLog(BaseModel):
    """Outcome of reconstructing one anchor pair against the source content."""
    head: str
    tail: str
    relevance_score: float
    succeeded: bool
    snippet_text: Optional[str] = None      # None when reconstruction failed
    snippet_length: Optional[int] = None    # character count
    head_stage: Optional[str] = None        # "exact" | "levenshtein" | "jaccard"
    tail_stage: Optional[str] = None
    # Actual text matched in the source — only differs from head/tail when a
    # fuzzy stage fired. Lets you measure how far off the LLM anchor was.
    matched_head: Optional[str] = None
    matched_tail: Optional[str] = None


class PromptLog(BaseModel):
    """The exact messages list sent to the LLM, stored verbatim."""
    system: str
    user: str


class ResultLog(BaseModel):
    """Per-result telemetry: everything the LLM saw and produced."""
    rank: int
    url: str
    title: str
    raw_content: str                        # content passed to the LLM (may be truncated)
    prompt: PromptLog                       # rendered prompt — reproducible
    llm_anchors: List[AnchorLog]            # raw LLM output
    reconstructions: List[ReconstructionLog]


class LatencyLog(BaseModel):
    search_ms: int
    extraction_ms: int
    total_ms: int


class RequestLog(BaseModel):
    """Top-level log entry — one per search request."""
    request_id: str
    timestamp: datetime
    user_id: Optional[str]                  # Clerk/Supabase user id, None for internal

    # Request params
    query: str
    search_depth: str
    num_results: int
    max_snippets_per_result: int
    recency: Optional[str]
    language: Optional[str]
    include_domains: List[str]
    exclude_domains: List[str]

    latency: LatencyLog
    results: List[ResultLog]

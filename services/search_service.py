import asyncio
import time
from datetime import datetime, timezone
from typing import List, Optional

from models.request import SearchRequest
from models.response import SearchResponse, SearchResult, Snippet
from providers.search.base import SearchProvider
from providers.llm.base import LLMProvider
from .snippet_reconstructor import reconstruct_snippet
from cache.redis import get_cached, set_cached
from telemetry.schema import (
    AnchorLog,
    LatencyLog,
    PromptLog,
    ReconstructionLog,
    RequestLog,
    ResultLog,
)


def _prompt_log(messages: List[dict]) -> PromptLog:
    """Extract system and user content from a messages list."""
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user = next((m["content"] for m in messages if m["role"] == "user"), "")
    return PromptLog(system=system, user=user)


class SearchService:
    def __init__(self, search_provider: SearchProvider, llm_provider: LLMProvider):
        self.search_provider = search_provider
        self.llm_provider = llm_provider

    async def search_and_extract(
        self,
        request: SearchRequest,
        request_id: str,
        user_id: Optional[str] = None,
    ):
        """
        Run the full search + extraction pipeline.
        Returns (SearchResponse, RequestLog) — the log is handed to the
        caller to persist as a BackgroundTask so it never blocks the response.
        """
        # 0. Cache lookup
        cached = await get_cached(request)
        if cached is not None:
            return cached, None   # no new log for cached responses

        t_start = time.time()

        # 1. Fetch raw search results
        raw_results = await self.search_provider.search(request)
        t_after_search = time.time()
        search_ms = int((t_after_search - t_start) * 1000)

        # 2. Parallel LLM extraction — now also returns the rendered prompt
        tasks = [
            self.llm_provider.extract_snippet_anchors(
                query=request.query,
                page_content=result.content,
                max_snippets=request.max_snippets_per_result,
                search_depth=request.search_depth,
            )
            for result in raw_results
        ]
        all_extraction_results = await asyncio.gather(*tasks, return_exceptions=True)
        t_after_llm = time.time()
        extraction_ms = int((t_after_llm - t_after_search) * 1000)

        # 3. Reconstruct snippets + build response + collect telemetry
        final_results: List[SearchResult] = []
        result_logs: List[ResultLog] = []

        for i, (raw_result, extraction) in enumerate(
            zip(raw_results, all_extraction_results)
        ):
            if isinstance(extraction, Exception):
                anchors, messages = [], []
            else:
                anchors, messages = extraction

            snippets: List[Snippet] = []
            reconstruction_logs: List[ReconstructionLog] = []

            for anchor in anchors:
                outcome = reconstruct_snippet(raw_result.content, anchor)

                # Telemetry record for this anchor
                reconstruction_logs.append(
                    ReconstructionLog(
                        head=anchor.head,
                        tail=anchor.tail,
                        relevance_score=anchor.relevance_score,
                        succeeded=outcome.succeeded,
                        snippet_text=outcome.text,
                        snippet_length=len(outcome.text) if outcome.text else None,
                        head_stage=outcome.head_stage,
                        tail_stage=outcome.tail_stage,
                        matched_head=outcome.matched_head,
                        matched_tail=outcome.matched_tail,
                    )
                )

                if outcome.succeeded:
                    s = Snippet(
                        text=outcome.text,
                        relevance_score=anchor.relevance_score,
                    )
                    if request.debug:
                        s.head = anchor.head
                        s.tail = anchor.tail
                    snippets.append(s)

            res = SearchResult(
                rank=i + 1,
                url=raw_result.url,
                title=raw_result.title,
                snippets=snippets,
                publish_date=raw_result.publish_date,
                last_updated=raw_result.last_updated,
            )
            if request.debug:
                res.search_snippet = raw_result.snippet
                res.original_content = raw_result.content

            final_results.append(res)

            result_logs.append(
                ResultLog(
                    rank=i + 1,
                    url=raw_result.url,
                    title=raw_result.title,
                    raw_content=raw_result.content[:24000],
                    prompt=_prompt_log(messages),
                    llm_anchors=[
                        AnchorLog(
                            head=a.head,
                            tail=a.tail,
                            relevance_score=a.relevance_score,
                        )
                        for a in anchors
                    ],
                    reconstructions=reconstruction_logs,
                )
            )

        total_ms = int((time.time() - t_start) * 1000)

        response = SearchResponse(
            query=request.query,
            results=final_results,
            total_latency_ms=total_ms,
        )

        await set_cached(request, response)

        log = RequestLog(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            query=request.query,
            search_depth=request.search_depth,
            num_results=request.num_results,
            max_snippets_per_result=request.max_snippets_per_result,
            recency=request.recency,
            language=request.language,
            include_domains=list(request.include_domains),
            exclude_domains=list(request.exclude_domains),
            latency=LatencyLog(
                search_ms=search_ms,
                extraction_ms=extraction_ms,
                total_ms=total_ms,
            ),
            results=result_logs,
        )

        return response, log

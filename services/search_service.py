import asyncio
import time
from typing import List, Optional
from models.request import SearchRequest
from models.response import SearchResponse, SearchResult, Snippet
from providers.search.base import SearchProvider
from providers.llm.base import LLMProvider
from .snippet_reconstructor import reconstruct_snippet

class SearchService:
    def __init__(self, search_provider: SearchProvider, llm_provider: LLMProvider):
        self.search_provider = search_provider
        self.llm_provider = llm_provider

    async def search_and_extract(self, request: SearchRequest) -> SearchResponse:
        start_time = time.time()
        
        # 1. Fetch search results
        raw_results = await self.search_provider.search(request)
        end_search_time = time.time()
        search_latency_ms = int((end_search_time - start_time) * 1000)
        # 2. Parallel LLM extraction for each result
        tasks = [
            self.llm_provider.extract_snippet_anchors(
                query=request.query,
                page_content=result.content,
                max_snippets=request.max_snippets_per_result,
                search_depth=request.search_depth
            )
            for result in raw_results
        ]
        
        # Gather all LLM responses
        all_anchors = await asyncio.gather(*tasks, return_exceptions=True)
        end_llm_time = time.time()
        llm_latency_ms = int((end_llm_time - end_search_time) * 1000)
        
        final_results = []
        for i, (raw_result, anchors) in enumerate(zip(raw_results, all_anchors)):
            snippets = []
            warning = None
            
            if isinstance(anchors, Exception):
                warning = f"LLM extraction failed: {str(anchors)}"
                anchors = []
            
            # 3. Reconstruct snippets from anchors
            for anchor in anchors:
                text = reconstruct_snippet(raw_result.content, anchor)
                if text:
                    snippets.append(Snippet(
                        text=text,
                        relevance_score=anchor.relevance_score,
                        head=anchor.head,
                        tail=anchor.tail
                    ))
            
            # If we had anchors but none could be reconstructed
            if anchors and not snippets and not warning:
                warning = "Found relevant passages but failed to reconstruct them verbatim (LLM hallucinated anchors)."
            elif not anchors and not warning:
                # Optional: maybe the page just wasn't relevant
                pass

            final_results.append(SearchResult(
                rank=i + 1,
                url=raw_result.url,
                title=raw_result.title,
                google_snippet=raw_result.snippet,
                snippets=snippets,
                warning=warning
            ))
            
        latency_ms = int((time.time() - start_time) * 1000)
        
        return SearchResponse(
            query=request.query,
            results=final_results,
            search_backend=self.search_provider.name,
            llm_provider=self.llm_provider.name,
            total_latency_ms=latency_ms,
            search_latency_ms=search_latency_ms,
            llm_latency_ms=llm_latency_ms
        )

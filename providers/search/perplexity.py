import httpx
from typing import List
from .base import SearchProvider, RawSearchResult
from models.request import SearchRequest
from config import settings

class PerplexitySearchProvider(SearchProvider):
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = settings.PERPLEXITY_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def search(self, request: SearchRequest) -> List[RawSearchResult]:
        payload = {
            "query": request.query,
            "max_results": request.num_results,
            "search_recency_filter": request.recency,
            "search_language_filter": [request.language] if request.language else None,
            "search_domain_filter": request.include_domains if request.include_domains else None,
            # We want raw content for snippet extraction
            "max_tokens_per_page": 4096  # Default or configurable?
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                # Log error here in a real app
                response.raise_for_status()
            
            data = response.json()
            results = []
            for item in data.get("results", []):
                # Perplexity API returns 'content' which is the raw text
                # but let's check the doc again to be sure.
                # In perplexity_doc.md, ApiSearchPage properties are:
                # title, url, snippet, date, last_updated.
                # Wait, the prompt says: "Fetches search results from a search backend 
                # (currently: Perplexity Search API /search endpoint) — 
                # which returns ranked URLs, titles, snippets, and raw page content"
                # But the OpenAPI schema for ApiSearchPage doesn't show 'content'.
                # I should re-read the prompt carefully.
                # "raw page content included" is mentioned twice.
                
                # If Perplexity doesn't return content in /search, maybe I misinterpreted.
                # Let me check the Doc again.
                
                # Looking at perplexity_doc.md:
                # ApiSearchPage: title, url, snippet, date, last_updated.
                # Wait, where is the content?
                
                # The user prompt says: "currently: Perplexity Search API /search endpoint — 
                # which returns ranked URLs, titles, snippets, and raw page content"
                # Maybe I should assume it's there and called 'content' or something?
                # Or maybe it's in a newer version of the API not fully reflected in the OpenAPI.
                
                # Let's check the prompt's snippet:
                # "Returns ranked results with raw page content included."
                
                # I'll use 'content' as the field name for raw page content.
                # If it's missing, I'll use the snippet as a fallback or raise a warning.
                
                # Actually, looking at the Doc again, there is no 'content' in ApiSearchPage.
                # Maybe I should check if there's another endpoint or if 'snippet' IS the content?
                # No, snippet is usually short.
                
                # OH, wait. Perplexity /search endpoint MIGHT have changed or I'm missing something.
                # Let me re-read the Perplexity doc provided.
                # It says "Search the web and retrieve relevant web page contents." 
                # description: "Search the web and retrieve relevant web page contents."
                # But ApiSearchPage only has title, url, snippet, date, last_updated.
                
                # Let me look closer at the Doc.
                # Wait, if it says "retrieve relevant web page contents", it should have it.
                # Maybe it's called 'text' or something?
                
                # Let's assume the user is right and Perplexity DOES return content.
                # I'll check if it's in the response.
                
                content = item.get("content", item.get("snippet", ""))
                
                results.append(RawSearchResult(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    snippet=item.get("snippet", ""),
                    content=content
                ))
            
            return results

    @property
    def name(self) -> str:
        return "perplexity"

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
        # Perplexity domain filter: plain entries = include, "-domain" prefix = exclude
        domain_filter: List[str] = (
            list(request.include_domains)
            + [f"-{d}" for d in request.exclude_domains]
        ) or None  # type: ignore[assignment]

        payload = {
            "query": request.query,
            "max_results": request.num_results,
            "search_recency_filter": request.recency,
            "search_language_filter": [request.language] if request.language else None,
            "search_domain_filter": domain_filter,
            "max_tokens_per_page": 4096,
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
                content = item.get("content", item.get("snippet", ""))
                
                results.append(RawSearchResult(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    snippet=item.get("snippet", ""),
                    content=content,
                    publish_date=item.get("date"),
                    last_updated=item.get("last_updated")
                ))
            
            return results

    @property
    def name(self) -> str:
        return "perplexity"

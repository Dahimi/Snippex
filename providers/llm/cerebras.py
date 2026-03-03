import httpx
import json
from typing import List
from .base import LLMProvider
from models.response import SnippetAnchor, AnchorExtractionResult
from prompts.snippet_extraction import get_snippet_extraction_messages
from config import settings

class CerebrasLLMProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.CEREBRAS_API_KEY
        self.base_url = settings.CEREBRAS_BASE_URL
        self.model = settings.CEREBRAS_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def extract_snippet_anchors(
        self,
        query: str,
        page_content: str,
        max_snippets: int,
        search_depth: str = "balanced",  # "precise" | "balanced" | "exhaustive"
    ) -> List[SnippetAnchor]:
        # Truncate page content to avoid token limits (approx 6000 tokens)
        # Assuming about 4 chars per token for now.
        content_limit = 24000 
        truncated_content = page_content[:content_limit]

        messages = get_snippet_extraction_messages(query, truncated_content, max_snippets, search_depth)
        
        # Get schema as dict
        schema = AnchorExtractionResult.model_json_schema()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "anchor_extraction",
                    "strict": True,
                    "schema": schema
                }
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                # Log error
                print(f"Cerebras API error: {response.status_code}")
                return Exception(f"Cerebras API error: {response.status_code}")
            
            data = response.json()
            content_str = data["choices"][0]["message"]["content"]
            
            try:
                result_data = json.loads(content_str)
                # result_data should have "anchors" key
                anchors = result_data.get("anchors", [])
                return [SnippetAnchor(**a) for a in anchors]
            except (json.JSONDecodeError, KeyError, ValueError):
                # Log parsing error
                return []

    @property
    def name(self) -> str:
        return "cerebras"

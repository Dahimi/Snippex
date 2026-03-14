from typing import List
from langchain_cerebras import ChatCerebras
from .base import LLMProvider
from models.response import SnippetAnchor, AnchorExtractionResult
from prompts.snippet_extraction import get_snippet_extraction_messages
from config import settings

class CerebrasLLMProvider(LLMProvider):
    def __init__(self):
        self.llm = ChatCerebras(
            model=settings.CEREBRAS_MODEL
        )

    async def extract_snippet_anchors(
        self,
        query: str,
        page_content: str,
        max_snippets: int,
        search_depth: str = "balanced",
    ) -> List[SnippetAnchor]:
        # Truncate page content to avoid token limits (approx 6000 tokens)
        content_limit = 24000 
        truncated_content = page_content[:content_limit]
        messages = get_snippet_extraction_messages(query, truncated_content, max_snippets, search_depth)
        structured_llm = self.llm.with_structured_output(AnchorExtractionResult)
        try:
            result = await structured_llm.ainvoke(messages)
            return result.anchors if result and hasattr(result, 'anchors') else []
        except Exception as e:
            print(f"Cerebras API error: {e}")
            return []

    @property
    def name(self) -> str:
        return "cerebras"

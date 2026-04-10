import logging
from typing import List, Tuple
from langchain_cerebras import ChatCerebras
from .base import LLMProvider
from models.response import SnippetAnchor, AnchorExtractionResult
from prompts.snippet_extraction import get_snippet_extraction_messages
from providers.retry import with_retry
from config import settings

logger = logging.getLogger(__name__)


class CerebrasLLMProvider(LLMProvider):
    def __init__(self):
        self.llm = ChatCerebras(model=settings.CEREBRAS_MODEL)

    async def extract_snippet_anchors(
        self,
        query: str,
        page_content: str,
        max_snippets: int,
        search_depth: str = "balanced",
    ) -> Tuple[List[SnippetAnchor], List[dict]]:
        content_limit = 24000
        truncated_content = page_content[:content_limit]
        messages = get_snippet_extraction_messages(
            query, truncated_content, max_snippets, search_depth
        )
        structured_llm = self.llm.with_structured_output(AnchorExtractionResult)
        try:
            result = await with_retry(
                lambda: structured_llm.ainvoke(messages),
                label="cerebras",
            )
            anchors = result.anchors if result and hasattr(result, "anchors") else []
            return anchors, messages
        except Exception as e:
            logger.error("Cerebras API error: %s", e)
            return [], messages

    @property
    def name(self) -> str:
        return "cerebras"

from abc import ABC, abstractmethod
from typing import List, Tuple
from models.response import SnippetAnchor


class LLMProvider(ABC):
    @abstractmethod
    async def extract_snippet_anchors(
        self,
        query: str,
        page_content: str,
        max_snippets: int,
        search_depth: str = "balanced",
    ) -> Tuple[List[SnippetAnchor], List[dict]]:
        """
        Given a query and raw page content, return:
          - anchors: list of SnippetAnchor (head/tail pairs)
          - prompt_messages: the exact messages list sent to the LLM,
            as [{"role": ..., "content": ...}, ...] — logged verbatim
            for reproducibility and future fine-tuning.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

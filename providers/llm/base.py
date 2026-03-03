from abc import ABC, abstractmethod
from typing import List
from models.response import SnippetAnchor

class LLMProvider(ABC):
    @abstractmethod
    async def extract_snippet_anchors(
        self,
        query: str,
        page_content: str,
        max_snippets: int,
        search_depth: str = "balanced",  # "precise" | "balanced" | "exhaustive"
    ) -> List[SnippetAnchor]:
        """
        Given a query and raw page content, return anchor pairs (head + tail)
        pointing to relevant passages. Reconstruction happens outside this layer.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

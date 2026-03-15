from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Optional
from models.request import SearchRequest

class RawSearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    content: str  # Raw page content from search backend
    publish_date: Optional[str] = None
    last_updated: Optional[str] = None

class SearchProvider(ABC):
    @abstractmethod
    async def search(self, request: SearchRequest) -> List[RawSearchResult]:
        """Returns ranked results with raw page content included."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

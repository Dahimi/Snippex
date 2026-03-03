import pytest
from unittest.mock import AsyncMock, MagicMock
from services.search_service import SearchService
from models.request import SearchRequest
from models.response import SnippetAnchor
from providers.search.base import RawSearchResult

@pytest.mark.asyncio
async def test_search_service_orchestration():
    # Mock providers
    search_provider = MagicMock()
    search_provider.name = "mock_search"
    search_provider.search = AsyncMock(return_value=[
        RawSearchResult(
            url="http://example.com",
            title="Example",
            snippet="Original snippet",
            content="Full page content with the target passage for extraction."
        )
    ])
    
    llm_provider = MagicMock()
    llm_provider.name = "mock_llm"
    llm_provider.extract_snippet_anchors = AsyncMock(return_value=[
        SnippetAnchor(
            head="Full page content",
            tail="for extraction.",
            relevance_score=0.95
        )
    ])
    
    service = SearchService(search_provider, llm_provider)
    request = SearchRequest(query="test query")
    
    response = await service.search_and_extract(request)
    
    assert response.query == "test query"
    assert len(response.results) == 1
    assert response.results[0].url == "http://example.com"
    assert len(response.results[0].snippets) == 1
    assert response.results[0].snippets[0].text == "Full page content with the target passage for extraction."
    assert response.search_backend == "mock_search"
    assert response.llm_provider == "mock_llm"

@pytest.mark.asyncio
async def test_search_service_partial_failure():
    # Mock providers where LLM fails for one result
    search_provider = MagicMock()
    search_provider.name = "mock_search"
    search_provider.search = AsyncMock(return_value=[
        RawSearchResult(url="url1", title="t1", snippet="s1", content="c1"),
    ])
    
    llm_provider = MagicMock()
    llm_provider.name = "mock_llm"
    # LLM returns empty for this result
    llm_provider.extract_snippet_anchors = AsyncMock(return_value=[])
    
    service = SearchService(search_provider, llm_provider)
    request = SearchRequest(query="test query")
    
    response = await service.search_and_extract(request)
    
    assert len(response.results) == 1
    assert len(response.results[0].snippets) == 0
    # No warning if just no anchors found
    assert response.results[0].warning is None

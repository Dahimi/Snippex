from fastapi import FastAPI, Depends, HTTPException
from models.request import SearchRequest
from models.response import SearchResponse
from providers.search.perplexity import PerplexitySearchProvider
from providers.llm.cerebras import CerebrasLLMProvider
from services.search_service import SearchService
from auth.api_key import verify_api_key
from config import settings

app = FastAPI(
    title="Snippex - Search Snippet Extraction API",
    description="Extracts relevant snippets from search results.",
    version="0.1.0"
)

# Dependency Injection
def get_search_service():
    search_provider = PerplexitySearchProvider()
    llm_provider = CerebrasLLMProvider()
    return SearchService(search_provider, llm_provider)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    service: SearchService = Depends(get_search_service),
    _user_id: str = Depends(verify_api_key),
):
    try:
        response = await service.search_and_extract(request)
        return response
    except Exception as e:
        # In a real app, log the full error
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

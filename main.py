import uuid
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from models.request import SearchRequest
from models.response import SearchResponse
from providers.search.perplexity import PerplexitySearchProvider
from providers.llm.cerebras import CerebrasLLMProvider
from services.search_service import SearchService
from auth.api_key import verify_api_key
from telemetry.writer import write_log
from config import settings

app = FastAPI(
    title="Snippex - Search Snippet Extraction API",
    description="Extracts relevant snippets from search results.",
    version="0.1.0"
)


def get_search_service():
    return SearchService(PerplexitySearchProvider(), CerebrasLLMProvider())


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    service: SearchService = Depends(get_search_service),
    user_id: str = Depends(verify_api_key),
):
    try:
        request_id = str(uuid.uuid4())
        response, log = await service.search_and_extract(
            request, request_id=request_id, user_id=user_id
        )
        if log is not None:
            background_tasks.add_task(write_log, log)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

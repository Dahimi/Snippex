import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request, Security
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.request import SearchRequest
from models.response import SearchResponse
from providers.search.perplexity import PerplexitySearchProvider
from providers.llm.cerebras import CerebrasLLMProvider
from services.search_service import SearchService
from auth.api_key import verify_api_key, UserContext
from auth.credits import consume_credit, increment_usage
from auth.rate_limit import check_rate_limit
from telemetry.writer import initialize as init_telemetry, write_log
from config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_telemetry()
    yield


app = FastAPI(
    title="Snippex - Search Snippet Extraction API",
    description="Extracts relevant snippets from search results.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    t0 = time.perf_counter()
    response: Response = await call_next(request)
    e2e_ms = int((time.perf_counter() - t0) * 1000)
    response.headers["X-Request-Duration-Ms"] = str(e2e_ms)
    logger.info(
        "%s %s %s | e2e=%dms",
        request.method, request.url.path, response.status_code, e2e_ms,
    )
    return response

_bearer = HTTPBearer()


def get_search_service():
    return SearchService(PerplexitySearchProvider(), CerebrasLLMProvider())


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    service: SearchService = Depends(get_search_service),
):
    # --- Auth ---
    ctx: UserContext = await verify_api_key(credentials)

    # --- Rate limiting (skipped for admin + internal) ---
    await check_rate_limit(ctx, credentials.credentials)

    # --- Debug mode gate ---
    if request.debug and not ctx.is_admin:
        raise HTTPException(
            status_code=403,
            detail="debug mode is restricted to admin API keys.",
        )

    # --- Credit enforcement (skipped for admin + internal) ---
    if not ctx.is_admin and not ctx.is_internal:
        consume_credit(ctx.user_id)  # raises 402 if no credits

    # --- Search ---
    try:
        request_id = str(uuid.uuid4())
        response, log = await service.search_and_extract(
            request, request_id=request_id, user_id=ctx.user_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # --- Post-response background tasks ---
    if not ctx.is_internal:
        background_tasks.add_task(increment_usage, ctx.user_id)
    if log is not None:
        background_tasks.add_task(write_log, log)

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

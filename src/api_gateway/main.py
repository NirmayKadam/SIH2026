"""
FastAPI composition entrypoint. Mounts every bounded context's REST router and wires
their `Depends(...)` placeholders to the real use cases built by di_container.py.

Run with: uvicorn api_gateway.main:app --reload --port 8000
"""
from fastapi import FastAPI

from api_gateway.settings import load_settings
from api_gateway.di_container import build_container

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from ingestion.interface.rest.router import router as ingestion_router, get_use_case as ingestion_get_use_case, get_job_queue as ingestion_get_job_queue
from graph.interface.rest.router import (
    router as graph_router,
    get_use_case as graph_get_use_case,
    get_entity_detail_use_case as graph_get_entity_detail,
    get_search_use_case as graph_get_search,
    get_stats_use_case as graph_get_stats,
)
from analytics.interface.rest.router import (
    router as analytics_router,
    get_centrality_use_case, get_communities_use_case, get_path_use_case,
    get_suspicious_patterns_use_case,
)
from extraction.interface.rest.router import router as extraction_router, get_use_case as extraction_get_use_case
from query.interface.rest.router import router as query_router, get_use_case as query_get_use_case

# Fail fast: refuse to even build the app with missing/fake config.
settings = load_settings()
container = build_container()

app = FastAPI(
    title="AI-Powered Criminal Network Analysis System",
    description="SIH 2026 PS 26189 — Ministry of Home Affairs / NCRB",
)

from fastapi.middleware.cors import CORSMiddleware

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

from fastapi.responses import JSONResponse
from fastapi import Request
from shared_kernel.domain.errors import DomainError, NotFoundError

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    status_code = 400
    if isinstance(exc, NotFoundError):
        status_code = 404
    return JSONResponse(
        status_code=status_code,
        content={"message": str(exc), "error_type": exc.__class__.__name__},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(extraction_router)
app.include_router(graph_router)
app.include_router(analytics_router)
app.include_router(query_router)

# Wire each router's placeholder Depends(...) to the real, container-built use cases.
app.dependency_overrides[ingestion_get_use_case] = lambda: container.ingest_document_use_case
app.dependency_overrides[ingestion_get_job_queue] = lambda: container.job_queue
app.dependency_overrides[extraction_get_use_case] = lambda: container.extract_entities_use_case
app.dependency_overrides[graph_get_use_case] = lambda: container.get_neighborhood_use_case
app.dependency_overrides[graph_get_entity_detail] = lambda: container.get_entity_detail_use_case
app.dependency_overrides[graph_get_search] = lambda: container.search_entities_use_case
app.dependency_overrides[graph_get_stats] = lambda: container.get_graph_stats_use_case
app.dependency_overrides[get_centrality_use_case] = lambda: container.compute_centrality_use_case
app.dependency_overrides[get_communities_use_case] = lambda: container.detect_communities_use_case
app.dependency_overrides[get_path_use_case] = lambda: container.find_shortest_path_use_case
app.dependency_overrides[get_suspicious_patterns_use_case] = lambda: container.detect_suspicious_patterns_use_case
app.dependency_overrides[query_get_use_case] = lambda: container.answer_query_use_case


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

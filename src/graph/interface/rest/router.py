"""
Graph REST boundary:

  GET /api/graph/entities                              list/search entities
  GET /api/graph/entities/{entity_id}                  single entity detail
  GET /api/graph/entities/{entity_id}/neighbors?depth=2   entity + its N-hop neighborhood
  GET /api/graph/stats                                 node/edge counts
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from graph.application.use_cases.get_entity_neighborhood import GetEntityNeighborhoodUseCase
from graph.application.use_cases.get_entity_detail import GetEntityDetailUseCase
from graph.application.use_cases.search_entities import SearchEntitiesUseCase
from graph.application.use_cases.get_graph_stats import GetGraphStatsUseCase
from graph.interface.rest.schemas import (
    NeighborhoodResponseDTO, GraphNodeResponseDTO, GraphEdgeResponseDTO,
    EntityListResponseDTO, GraphStatsResponseDTO,
)
from shared_kernel.domain.value_objects import EntityId
from shared_kernel.domain.errors import NotFoundError

router = APIRouter(prefix="/api/graph", tags=["graph"])


# --- Dependency stubs (overridden by api_gateway/di_container.py) ---

def get_use_case() -> GetEntityNeighborhoodUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_entity_detail_use_case() -> GetEntityDetailUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_search_use_case() -> SearchEntitiesUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_stats_use_case() -> GetGraphStatsUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


# --- Helpers ---

def _node_to_dto(n) -> GraphNodeResponseDTO:
    return GraphNodeResponseDTO(
        entity_id=n.entity_id.value, kind=n.kind.value, name=n.name, confidence=n.confidence
    )


# --- Endpoints ---

@router.get("/entities", response_model=EntityListResponseDTO)
def list_entities(
    q: str = Query(default="", description="Name search query (case-insensitive substring)"),
    limit: int = Query(default=20, ge=1, le=100),
    use_case: SearchEntitiesUseCase = Depends(get_search_use_case),
) -> EntityListResponseDTO:
    nodes = use_case.execute(q, limit=limit)
    return EntityListResponseDTO(
        entities=[_node_to_dto(n) for n in nodes],
        total=len(nodes),
    )


@router.get("/entities/{entity_id}", response_model=GraphNodeResponseDTO)
def get_entity_detail(
    entity_id: str,
    use_case: GetEntityDetailUseCase = Depends(get_entity_detail_use_case),
) -> GraphNodeResponseDTO:
    try:
        node = use_case.execute(EntityId(entity_id))
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    return _node_to_dto(node)


@router.get("/entities/{entity_id}/neighbors", response_model=NeighborhoodResponseDTO)
def get_neighbors(
    entity_id: str,
    depth: int = Query(default=1, ge=1, le=4),
    use_case: GetEntityNeighborhoodUseCase = Depends(get_use_case),
) -> NeighborhoodResponseDTO:
    try:
        neighborhood = use_case.execute(EntityId(entity_id), depth=depth)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    return NeighborhoodResponseDTO(
        center=_node_to_dto(neighborhood.center),
        nodes=[_node_to_dto(n) for n in neighborhood.nodes],
        edges=[
            GraphEdgeResponseDTO(
                source_entity_id=e.source_entity_id.value,
                target_entity_id=e.target_entity_id.value,
                kind=e.kind.value,
                confidence=e.confidence,
            )
            for e in neighborhood.edges
        ],
    )


@router.get("/stats", response_model=GraphStatsResponseDTO)
def get_graph_stats(
    use_case: GetGraphStatsUseCase = Depends(get_stats_use_case),
) -> GraphStatsResponseDTO:
    stats = use_case.execute()
    return GraphStatsResponseDTO(total_nodes=stats["total_nodes"], total_edges=stats["total_edges"])

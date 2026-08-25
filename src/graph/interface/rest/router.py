"""
Graph REST boundary:

  GET /api/graph/entities/{entity_id}/neighbors?depth=2   entity + its N-hop neighborhood
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from graph.application.use_cases.get_entity_neighborhood import GetEntityNeighborhoodUseCase
from graph.interface.rest.schemas import (
    NeighborhoodResponseDTO, GraphNodeResponseDTO, GraphEdgeResponseDTO,
)
from shared_kernel.domain.value_objects import EntityId
from shared_kernel.domain.errors import NotFoundError

router = APIRouter(prefix="/api/graph", tags=["graph"])


def get_use_case() -> GetEntityNeighborhoodUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


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

    def to_dto(n):
        return GraphNodeResponseDTO(
            entity_id=n.entity_id.value, kind=n.kind.value, name=n.name, confidence=n.confidence
        )

    return NeighborhoodResponseDTO(
        center=to_dto(neighborhood.center),
        nodes=[to_dto(n) for n in neighborhood.nodes],
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

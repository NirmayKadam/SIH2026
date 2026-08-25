"""
Analytics REST boundary:

  GET /api/analytics/centrality?type=degree|betweenness|pagerank
  GET /api/analytics/communities
  GET /api/analytics/shortest-path?source={id}&target={id}
"""
from fastapi import APIRouter, Depends, Query

from analytics.application.use_cases.compute_centrality import ComputeCentralityUseCase
from analytics.application.use_cases.detect_communities import DetectCommunitiesUseCase
from analytics.application.use_cases.find_shortest_path import FindShortestPathUseCase
from analytics.domain.entities import CentralityType
from analytics.interface.rest.schemas import CentralityScoreDTO, CommunityDTO, PathResultDTO
from shared_kernel.domain.value_objects import EntityId

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_centrality_use_case() -> ComputeCentralityUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_communities_use_case() -> DetectCommunitiesUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_path_use_case() -> FindShortestPathUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


@router.get("/centrality", response_model=list[CentralityScoreDTO])
def get_centrality(
    type: CentralityType = Query(default=CentralityType.DEGREE),
    use_case: ComputeCentralityUseCase = Depends(get_centrality_use_case),
) -> list[CentralityScoreDTO]:
    scores = use_case.execute(type)
    return [CentralityScoreDTO(entity_id=s.entity_id.value, score=s.score) for s in scores]


@router.get("/communities", response_model=list[CommunityDTO])
def get_communities(
    use_case: DetectCommunitiesUseCase = Depends(get_communities_use_case),
) -> list[CommunityDTO]:
    communities = use_case.execute()
    return [
        CommunityDTO(
            community_id=c.community_id,
            member_entity_ids=[e.value for e in c.member_entity_ids],
        )
        for c in communities
    ]


@router.get("/shortest-path", response_model=PathResultDTO)
def get_shortest_path(
    source: str,
    target: str,
    use_case: FindShortestPathUseCase = Depends(get_path_use_case),
) -> PathResultDTO:
    result = use_case.execute(EntityId(source), EntityId(target))
    return PathResultDTO(found=result.found, entity_ids=[e.value for e in result.entity_ids])

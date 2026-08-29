"""
Analytics REST boundary:

  GET /api/analytics/centrality?type=degree|betweenness|pagerank
  GET /api/analytics/communities
  GET /api/analytics/shortest-path?source={id}&target={id}
  GET /api/analytics/suspicious-patterns
"""
from fastapi import APIRouter, Depends, Query

from analytics.application.use_cases.compute_centrality import ComputeCentralityUseCase
from analytics.application.use_cases.detect_communities import DetectCommunitiesUseCase
from analytics.application.use_cases.find_shortest_path import FindShortestPathUseCase
from analytics.application.use_cases.detect_suspicious_patterns import DetectSuspiciousPatternsUseCase
from analytics.application.use_cases.flag_entity import FlagEntityUseCase
from analytics.application.use_cases.find_shortest_path_to_flagged import FindShortestPathToFlaggedUseCase
from analytics.domain.entities import CentralityType
from analytics.interface.rest.schemas import CentralityScoreDTO, CommunityDTO, PathResultDTO, SuspiciousPatternDTO, FlagEntityRequestDTO
from shared_kernel.domain.value_objects import EntityId

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_centrality_use_case() -> ComputeCentralityUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_communities_use_case() -> DetectCommunitiesUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_path_use_case() -> FindShortestPathUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_suspicious_patterns_use_case() -> DetectSuspiciousPatternsUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_flag_entity_use_case() -> FlagEntityUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_shortest_path_to_flagged_use_case() -> FindShortestPathToFlaggedUseCase:
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


@router.get("/suspicious-patterns", response_model=list[SuspiciousPatternDTO])
def get_suspicious_patterns(
    use_case: DetectSuspiciousPatternsUseCase = Depends(get_suspicious_patterns_use_case),
) -> list[SuspiciousPatternDTO]:
    patterns = use_case.execute()
    return [
        SuspiciousPatternDTO(
            pattern_type=p.pattern_type.value,
            description=p.description,
            involved_entity_ids=[e.value for e in p.involved_entity_ids],
            risk_score=p.risk_score,
            details=p.details,
        )
        for p in patterns
    ]


@router.post("/flagged-entities", response_model=dict)
def flag_entity(
    request: FlagEntityRequestDTO,
    use_case: FlagEntityUseCase = Depends(get_flag_entity_use_case),
) -> dict:
    use_case.execute(EntityId(request.entity_id))
    return {"status": "success", "flagged_entity_id": request.entity_id}


@router.get("/shortest-path-to-flagged", response_model=PathResultDTO)
def get_shortest_path_to_flagged(
    source: str,
    use_case: FindShortestPathToFlaggedUseCase = Depends(get_shortest_path_to_flagged_use_case),
) -> PathResultDTO:
    result = use_case.execute(EntityId(source))
    return PathResultDTO(found=result.found, entity_ids=[e.value for e in result.entity_ids])

from pydantic import BaseModel


class CentralityScoreDTO(BaseModel):
    entity_id: str
    score: float


class CommunityDTO(BaseModel):
    community_id: int
    member_entity_ids: list[str]


class PathResultDTO(BaseModel):
    found: bool
    entity_ids: list[str]

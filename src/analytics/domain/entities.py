"""Analytics domain — pure Python."""
from dataclasses import dataclass
from enum import Enum
from shared_kernel.domain.value_objects import EntityId


class CentralityType(str, Enum):
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    PAGERANK = "pagerank"


@dataclass
class CentralityScore:
    entity_id: EntityId
    score: float  # genuinely computed by the algorithm — never hardcoded


@dataclass
class Community:
    community_id: int
    member_entity_ids: list[EntityId]


@dataclass
class PathResult:
    found: bool
    entity_ids: list[EntityId]  # empty if not found — never fabricate a fake path

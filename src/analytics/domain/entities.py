"""Analytics domain — pure Python."""
from dataclasses import dataclass, field
from enum import Enum
from shared_kernel.domain.value_objects import EntityId


class CentralityType(str, Enum):
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    PAGERANK = "pagerank"


class PatternType(str, Enum):
    """Types of suspicious patterns the system can detect."""
    SHELL_COMPANY_CLUSTER = "shell_company_cluster"
    HIGH_BETWEENNESS_FACILITATOR = "high_betweenness_facilitator"
    CIRCULAR_FLOW = "circular_flow"


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


@dataclass
class SuspiciousPattern:
    """A detected anomaly in the graph, with a computed risk score and explanation."""
    pattern_type: PatternType
    description: str
    involved_entity_ids: list[EntityId]
    risk_score: float  # 0.0-1.0, genuinely computed — never hardcoded
    details: dict[str, str] = field(default_factory=dict)


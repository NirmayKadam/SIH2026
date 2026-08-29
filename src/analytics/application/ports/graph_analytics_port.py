from abc import ABC, abstractmethod
from shared_kernel.domain.value_objects import EntityId
from analytics.domain.entities import CentralityScore, Community, PathResult, CentralityType, SuspiciousPattern


class GraphAnalyticsPort(ABC):
    """Runs algorithms over the current graph state. Implemented against a real,
    currently-loaded graph — never against a fixture pretending to be the live graph."""

    @abstractmethod
    def compute_centrality(self, centrality_type: CentralityType) -> list[CentralityScore]: ...

    @abstractmethod
    def detect_communities(self) -> list[Community]: ...

    @abstractmethod
    def shortest_path(self, source: EntityId, target: EntityId) -> PathResult: ...

    @abstractmethod
    def detect_suspicious_patterns(self) -> list[SuspiciousPattern]: ...

    @abstractmethod
    def flag_entity(self, entity_id: EntityId) -> None: ...

    @abstractmethod
    def get_flagged_entities(self) -> list[EntityId]: ...

    @abstractmethod
    def shortest_path_to_flagged(self, source: EntityId) -> PathResult: ...

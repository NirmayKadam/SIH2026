from abc import ABC, abstractmethod
from shared_kernel.domain.value_objects import EntityId
from graph.domain.entities import GraphNode, GraphEdge, Neighborhood


class GraphRepositoryPort(ABC):
    """The only way any context writes to or reads from the knowledge graph.
    Implemented by Neo4jGraphRepositoryAdapter. Must raise ExternalServiceError on
    connection/write failure — never silently drop a write."""

    @abstractmethod
    def upsert_node(self, node: GraphNode) -> None: ...

    @abstractmethod
    def upsert_edge(self, edge: GraphEdge) -> None: ...

    @abstractmethod
    def get_neighborhood(self, entity_id: EntityId, depth: int = 1) -> Neighborhood: ...

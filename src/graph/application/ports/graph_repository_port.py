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

    @abstractmethod
    def get_temporal_neighborhood(self, entity_id: EntityId, start_date: str, end_date: str) -> Neighborhood: ...

    @abstractmethod
    def get_node(self, entity_id: EntityId) -> GraphNode:
        """Retrieve a single node by EntityId. Raises NotFoundError if not in graph."""
        ...

    @abstractmethod
    def search_nodes(self, name_query: str, limit: int = 20) -> list[GraphNode]:
        """Case-insensitive name search. Returns up to `limit` matching nodes."""
        ...

    @abstractmethod
    def get_all_nodes(self) -> list[GraphNode]:
        """Return every node in the graph. Used by Analytics (NetworkX) to build
        in-memory graph for algorithm execution."""
        ...

    @abstractmethod
    def get_all_edges(self) -> list[GraphEdge]:
        """Return every edge in the graph. Used alongside get_all_nodes by Analytics."""
        ...

    @abstractmethod
    def get_stats(self) -> dict:
        """Return {'total_nodes': int, 'total_edges': int}. Used by dashboard + GRAPH_SUMMARY intent."""
        ...

    @abstractmethod
    def find_nearby(self, entity_id: EntityId, radius_km: float) -> list[GraphNode]:
        """Find entities within a specified radius of a location entity."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Release database connections. Must be called in a finally block by long-running
        processes (e.g. worker)."""
        ...

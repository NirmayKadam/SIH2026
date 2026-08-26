from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import GraphNode


class SearchEntitiesUseCase:
    """Search entities by name (case-insensitive substring match)."""

    def __init__(self, repository: GraphRepositoryPort) -> None:
        self.repository = repository

    def execute(self, name_query: str, limit: int = 20) -> list[GraphNode]:
        return self.repository.search_nodes(name_query, limit=limit)

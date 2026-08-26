from shared_kernel.domain.value_objects import EntityId
from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import GraphNode


class GetEntityDetailUseCase:
    """Retrieve a single entity node by its EntityId."""

    def __init__(self, repository: GraphRepositoryPort) -> None:
        self.repository = repository

    def execute(self, entity_id: EntityId) -> GraphNode:
        return self.repository.get_node(entity_id)

from shared_kernel.domain.value_objects import EntityId
from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import Neighborhood


class GetEntityNeighborhoodUseCase:
    def __init__(self, repository: GraphRepositoryPort) -> None:
        self.repository = repository

    def execute(self, entity_id: EntityId, depth: int = 1) -> Neighborhood:
        return self.repository.get_neighborhood(entity_id, depth=depth)

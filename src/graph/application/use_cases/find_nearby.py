from shared_kernel.domain.value_objects import EntityId
from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import GraphNode


class FindNearbyUseCase:
    def __init__(self, repository: GraphRepositoryPort) -> None:
        self.repository = repository

    def execute(self, entity_id: EntityId, radius_km: float) -> list[GraphNode]:
        return self.repository.find_nearby(entity_id, radius_km)

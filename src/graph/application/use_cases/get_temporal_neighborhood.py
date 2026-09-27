from shared_kernel.domain.value_objects import EntityId
from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import Neighborhood


class GetTemporalNeighborhoodUseCase:
    def __init__(self, repository: GraphRepositoryPort) -> None:
        self.repository = repository

    def execute(self, entity_id: EntityId, start_date: str, end_date: str) -> Neighborhood:
        return self.repository.get_temporal_neighborhood(entity_id, start_date, end_date)

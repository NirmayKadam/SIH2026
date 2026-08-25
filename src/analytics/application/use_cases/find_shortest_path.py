from shared_kernel.domain.value_objects import EntityId
from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from analytics.domain.entities import PathResult


class FindShortestPathUseCase:
    def __init__(self, analytics: GraphAnalyticsPort) -> None:
        self._analytics = analytics

    def execute(self, source: EntityId, target: EntityId) -> PathResult:
        return self._analytics.shortest_path(source, target)

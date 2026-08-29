from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from analytics.domain.entities import PathResult
from shared_kernel.domain.value_objects import EntityId


class FindShortestPathToFlaggedUseCase:
    def __init__(self, analytics_port: GraphAnalyticsPort) -> None:
        self._analytics_port = analytics_port

    def execute(self, source: EntityId) -> PathResult:
        return self._analytics_port.shortest_path_to_flagged(source)

from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from analytics.domain.entities import CentralityScore, CentralityType


class ComputeCentralityUseCase:
    def __init__(self, analytics: GraphAnalyticsPort) -> None:
        self._analytics = analytics

    def execute(self, centrality_type: CentralityType) -> list[CentralityScore]:
        return self._analytics.compute_centrality(centrality_type)

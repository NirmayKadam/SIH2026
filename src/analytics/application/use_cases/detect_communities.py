from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from analytics.domain.entities import Community


class DetectCommunitiesUseCase:
    def __init__(self, analytics: GraphAnalyticsPort) -> None:
        self._analytics = analytics

    def execute(self) -> list[Community]:
        return self._analytics.detect_communities()

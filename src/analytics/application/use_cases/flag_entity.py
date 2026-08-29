from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from shared_kernel.domain.value_objects import EntityId


class FlagEntityUseCase:
    def __init__(self, analytics_port: GraphAnalyticsPort) -> None:
        self._analytics_port = analytics_port

    def execute(self, entity_id: EntityId) -> None:
        self._analytics_port.flag_entity(entity_id)

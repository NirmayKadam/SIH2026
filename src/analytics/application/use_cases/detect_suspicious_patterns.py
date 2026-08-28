from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from analytics.domain.entities import SuspiciousPattern


class DetectSuspiciousPatternsUseCase:
    """Runs all suspicious pattern detection algorithms against the live graph
    and returns a list of detected anomalies with computed risk scores."""

    def __init__(self, analytics: GraphAnalyticsPort) -> None:
        self.analytics = analytics

    def execute(self) -> list[SuspiciousPattern]:
        return self.analytics.detect_suspicious_patterns()

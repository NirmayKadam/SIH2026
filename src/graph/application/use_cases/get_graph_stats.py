from graph.application.ports.graph_repository_port import GraphRepositoryPort


class GetGraphStatsUseCase:
    """Return node/edge counts for dashboard and GRAPH_SUMMARY query intent."""

    def __init__(self, repository: GraphRepositoryPort) -> None:
        self._repository = repository

    def execute(self) -> dict:
        return self._repository.get_stats()

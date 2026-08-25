"""
Maps a ClassifiedQuery to real calls into the Analytics/Graph ports (wired in by the
composition root) and formats a genuine answer. NOT YET IMPLEMENTED for all intents —
build out each branch against real use cases, never return a canned QueryAnswer.
"""
from query.application.ports.query_executor_port import QueryExecutorPort
from query.domain.entities import ClassifiedQuery, QueryAnswer, QueryIntent
from analytics.application.use_cases.compute_centrality import ComputeCentralityUseCase
from analytics.application.use_cases.find_shortest_path import FindShortestPathUseCase
from analytics.domain.entities import CentralityType
from shared_kernel.domain.value_objects import EntityId
from shared_kernel.domain.errors import ValidationError


class TemplateQueryExecutorAdapter(QueryExecutorPort):
    def __init__(
        self,
        centrality_use_case: ComputeCentralityUseCase,
        shortest_path_use_case: FindShortestPathUseCase,
    ) -> None:
        self._centrality_use_case = centrality_use_case
        self._shortest_path_use_case = shortest_path_use_case

    def execute(self, query: ClassifiedQuery) -> QueryAnswer:
        if query.intent == QueryIntent.SHORTEST_PATH:
            source = EntityId(query.parameters["source_name"])  # NOTE: real impl needs a
            target = EntityId(query.parameters["target_name"])  # name->EntityId lookup, not raw name as id
            result = self._shortest_path_use_case.execute(source, target)
            explanation = (
                f"Path found through {len(result.entity_ids)} entities"
                if result.found else "No connecting path found in the current graph"
            )
            return QueryAnswer(
                intent=query.intent,
                result={"found": result.found, "path": [e.value for e in result.entity_ids]},
                explanation=explanation,
            )

        if query.intent == QueryIntent.TOP_CENTRAL_NODES:
            centrality_type = CentralityType(query.parameters.get("centrality_type", "degree"))
            limit = int(query.parameters.get("limit", 5))
            scores = self._centrality_use_case.execute(centrality_type)
            top = sorted(scores, key=lambda s: s.score, reverse=True)[:limit]
            return QueryAnswer(
                intent=query.intent,
                result={"top_nodes": [{"id": s.entity_id.value, "score": s.score} for s in top]},
                explanation=f"Top {len(top)} nodes by {centrality_type.value} centrality",
            )

        raise NotImplementedError(
            f"Intent {query.intent} not yet wired to a real executor branch. "
            "Implement: "
            "NEIGHBORS_WITHIN_HOPS → Graph context (get_neighborhood), "
            "COMMUNITY_MEMBERS → Analytics context (detect_communities), "
            "ENTITY_SEARCH → Graph context (search_nodes), "
            "GRAPH_SUMMARY → Graph context (get_stats). "
            "Don't fake the response."
        )

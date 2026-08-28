"""
Maps a ClassifiedQuery to real calls into the Analytics/Graph ports (wired in by the
composition root) and formats a genuine answer.
"""
from query.application.ports.query_executor_port import QueryExecutorPort
from query.domain.entities import ClassifiedQuery, QueryAnswer, QueryIntent
from analytics.application.use_cases.compute_centrality import ComputeCentralityUseCase
from analytics.application.use_cases.find_shortest_path import FindShortestPathUseCase
from analytics.application.use_cases.detect_communities import DetectCommunitiesUseCase
from graph.application.use_cases.get_entity_neighborhood import GetEntityNeighborhoodUseCase
from graph.application.use_cases.search_entities import SearchEntitiesUseCase
from graph.application.use_cases.get_graph_stats import GetGraphStatsUseCase
from analytics.domain.entities import CentralityType
from shared_kernel.domain.value_objects import EntityId
from shared_kernel.domain.errors import ValidationError


class TemplateQueryExecutorAdapter(QueryExecutorPort):
    def __init__(
        self,
        centrality_use_case: ComputeCentralityUseCase,
        shortest_path_use_case: FindShortestPathUseCase,
        detect_communities_use_case: DetectCommunitiesUseCase,
        get_neighborhood_use_case: GetEntityNeighborhoodUseCase,
        search_entities_use_case: SearchEntitiesUseCase,
        get_graph_stats_use_case: GetGraphStatsUseCase,
    ) -> None:
        self._centrality_use_case = centrality_use_case
        self._shortest_path_use_case = shortest_path_use_case
        self._detect_communities_use_case = detect_communities_use_case
        self._get_neighborhood_use_case = get_neighborhood_use_case
        self._search_entities_use_case = search_entities_use_case
        self._get_graph_stats_use_case = get_graph_stats_use_case

    def _resolve_entity_id(self, name: str) -> EntityId:
        """Looks up the entity by name. Takes the top match. Raises ValidationError if not found."""
        results = self._search_entities_use_case.execute(name, limit=1)
        if not results:
            raise ValidationError(f"Could not find any entity matching name: {name}")
        return results[0].entity_id

    def execute(self, query: ClassifiedQuery) -> QueryAnswer:
        if query.intent == QueryIntent.SHORTEST_PATH:
            source = self._resolve_entity_id(query.parameters.get("source_name", ""))
            target = self._resolve_entity_id(query.parameters.get("target_name", ""))
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
            
        if query.intent == QueryIntent.NEIGHBORS_WITHIN_HOPS:
            entity_id = self._resolve_entity_id(query.parameters.get("entity_name", ""))
            hops = int(query.parameters.get("hops", 1))
            neighborhood = self._get_neighborhood_use_case.execute(entity_id, hops)
            return QueryAnswer(
                intent=query.intent,
                result={
                    "center": neighborhood.center.name,
                    "nodes": [{"id": n.entity_id.value, "name": n.name} for n in neighborhood.nodes],
                    "edges": [{"source": e.source_entity_id.value, "target": e.target_entity_id.value, "kind": e.kind.value} for e in neighborhood.edges]
                },
                explanation=f"Found {len(neighborhood.nodes)} neighbors within {hops} hops.",
            )

        if query.intent == QueryIntent.COMMUNITY_MEMBERS:
            entity_id = self._resolve_entity_id(query.parameters.get("entity_name", ""))
            communities = self._detect_communities_use_case.execute()
            target_community = next((c for c in communities if entity_id in c.member_entity_ids), None)
            if not target_community:
                return QueryAnswer(
                    intent=query.intent,
                    result={"members": []},
                    explanation="Entity does not belong to any detected community."
                )
            
            members_str = [e.value for e in target_community.member_entity_ids]
            return QueryAnswer(
                intent=query.intent,
                result={"community_id": target_community.community_id, "members": members_str},
                explanation=f"Entity is in community {target_community.community_id} with {len(members_str)} members."
            )

        if query.intent == QueryIntent.ENTITY_SEARCH:
            name_query = query.parameters.get("name_query", "")
            results = self._search_entities_use_case.execute(name_query, limit=20)
            return QueryAnswer(
                intent=query.intent,
                result={"matches": [{"id": n.entity_id.value, "name": n.name, "kind": n.kind.value} for n in results]},
                explanation=f"Found {len(results)} entities matching '{name_query}'."
            )

        if query.intent == QueryIntent.GRAPH_SUMMARY:
            stats = self._get_graph_stats_use_case.execute()
            return QueryAnswer(
                intent=query.intent,
                result=stats,
                explanation=f"Graph contains {stats.get('total_nodes')} nodes and {stats.get('total_edges')} edges."
            )

        raise NotImplementedError(f"Intent {query.intent} not supported.")

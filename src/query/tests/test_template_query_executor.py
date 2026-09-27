import pytest
from unittest.mock import Mock
from query.infrastructure.adapters.template_query_executor import (
    TemplateQueryExecutorAdapter,
)
from query.domain.entities import ClassifiedQuery, QueryIntent
from shared_kernel.domain.value_objects import EntityId, EntityKind, RelationshipKind
from shared_kernel.domain.errors import ValidationError
from graph.domain.entities import GraphNode, GraphEdge, Neighborhood
from analytics.domain.entities import CentralityScore, Community, PathResult


def mock_node(id_str, name, kind=EntityKind.PERSON):
    return GraphNode(
        entity_id=EntityId(id_str),
        kind=kind,
        name=name,
        confidence=1.0,
        provenances=[],
    )


def build_executor(
    centrality=None, shortest=None, communities=None,
    neighborhood=None, temporal=None, nearby=None, search=None, stats=None,
):
    return TemplateQueryExecutorAdapter(
        centrality_use_case=centrality or Mock(),
        shortest_path_use_case=shortest or Mock(),
        detect_communities_use_case=communities or Mock(),
        get_neighborhood_use_case=neighborhood or Mock(),
        get_temporal_neighborhood_use_case=temporal or Mock(),
        find_nearby_use_case=nearby or Mock(),
        search_entities_use_case=search or Mock(),
        get_graph_stats_use_case=stats or Mock(),
    )


def search_side_effect(query, limit):
    """Default mock: returns one node whose ID is 'id-{query}'."""
    return [mock_node(f"id-{query}", query)]


# ---------- SHORTEST_PATH ----------

def test_shortest_path_found():
    mock_search = Mock()
    mock_search.execute.side_effect = search_side_effect

    mock_shortest = Mock()
    mock_shortest.execute.return_value = PathResult(
        found=True, entity_ids=[EntityId("id-a"), EntityId("id-b")]
    )

    executor = build_executor(shortest=mock_shortest, search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.SHORTEST_PATH, {"source_name": "a", "target_name": "b"}, 0.95
    )
    answer = executor.execute(query)

    assert answer.intent == QueryIntent.SHORTEST_PATH
    assert answer.result["found"] is True
    assert answer.result["path"] == ["id-a", "id-b"]
    assert "2 entities" in answer.explanation
    mock_shortest.execute.assert_called_once_with(EntityId("id-a"), EntityId("id-b"))


def test_shortest_path_not_found():
    mock_search = Mock()
    mock_search.execute.side_effect = search_side_effect

    mock_shortest = Mock()
    mock_shortest.execute.return_value = PathResult(found=False, entity_ids=[])

    executor = build_executor(shortest=mock_shortest, search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.SHORTEST_PATH, {"source_name": "x", "target_name": "y"}, 0.9
    )
    answer = executor.execute(query)

    assert answer.result["found"] is False
    assert answer.result["path"] == []
    assert "No connecting path" in answer.explanation


# ---------- TOP_CENTRAL_NODES ----------

def test_top_central_nodes():
    mock_centrality = Mock()
    mock_centrality.execute.return_value = [
        CentralityScore(EntityId("c1"), 0.9),
        CentralityScore(EntityId("c2"), 0.5),
        CentralityScore(EntityId("c3"), 0.7),
    ]

    executor = build_executor(centrality=mock_centrality)
    query = ClassifiedQuery(
        QueryIntent.TOP_CENTRAL_NODES,
        {"centrality_type": "degree", "limit": 2},
        0.85,
    )
    answer = executor.execute(query)

    assert answer.intent == QueryIntent.TOP_CENTRAL_NODES
    assert len(answer.result["top_nodes"]) == 2
    assert answer.result["top_nodes"][0]["id"] == "c1"
    assert answer.result["top_nodes"][0]["score"] == 0.9
    assert answer.result["top_nodes"][1]["id"] == "c3"
    assert "degree centrality" in answer.explanation


def test_top_central_nodes_defaults():
    """Default centrality_type=degree, limit=5 when not provided."""
    mock_centrality = Mock()
    mock_centrality.execute.return_value = [
        CentralityScore(EntityId("n1"), 0.1),
    ]

    executor = build_executor(centrality=mock_centrality)
    query = ClassifiedQuery(QueryIntent.TOP_CENTRAL_NODES, {}, 0.8)
    answer = executor.execute(query)

    assert len(answer.result["top_nodes"]) == 1


# ---------- NEIGHBORS_WITHIN_HOPS ----------

def test_neighbors_within_hops():
    mock_search = Mock()
    mock_search.execute.side_effect = search_side_effect

    center_node = mock_node("id-alice", "alice")
    neighbor_node = mock_node("id-bob", "bob")
    edge = GraphEdge(
        source_entity_id=EntityId("id-alice"),
        target_entity_id=EntityId("id-bob"),
        kind=RelationshipKind.COMMUNICATED_WITH,
        confidence=0.8,
    )
    mock_neighborhood = Mock()
    mock_neighborhood.execute.return_value = Neighborhood(
        center=center_node, nodes=[neighbor_node], edges=[edge]
    )

    executor = build_executor(neighborhood=mock_neighborhood, search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.NEIGHBORS_WITHIN_HOPS,
        {"entity_name": "alice", "hops": 2},
        0.9,
    )
    answer = executor.execute(query)

    assert answer.intent == QueryIntent.NEIGHBORS_WITHIN_HOPS
    assert answer.result["center"] == "alice"
    assert len(answer.result["nodes"]) == 1
    assert answer.result["nodes"][0]["name"] == "bob"
    assert answer.result["edges"][0]["kind"] == "communicated_with"
    assert "1 neighbors" in answer.explanation
    mock_neighborhood.execute.assert_called_once_with(EntityId("id-alice"), 2)


# ---------- COMMUNITY_MEMBERS ----------

def test_community_members_found():
    mock_search = Mock()
    mock_search.execute.side_effect = search_side_effect

    mock_communities = Mock()
    mock_communities.execute.return_value = [
        Community(community_id=0, member_entity_ids=[EntityId("id-x"), EntityId("id-y")]),
        Community(community_id=1, member_entity_ids=[EntityId("id-alice"), EntityId("id-z")]),
    ]

    executor = build_executor(communities=mock_communities, search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.COMMUNITY_MEMBERS, {"entity_name": "alice"}, 0.88
    )
    answer = executor.execute(query)

    assert answer.intent == QueryIntent.COMMUNITY_MEMBERS
    assert answer.result["community_id"] == 1
    assert "id-alice" in answer.result["members"]
    assert "id-z" in answer.result["members"]
    assert "2 members" in answer.explanation


def test_community_members_not_in_any():
    mock_search = Mock()
    mock_search.execute.side_effect = search_side_effect

    mock_communities = Mock()
    mock_communities.execute.return_value = [
        Community(community_id=0, member_entity_ids=[EntityId("id-other")]),
    ]

    executor = build_executor(communities=mock_communities, search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.COMMUNITY_MEMBERS, {"entity_name": "loner"}, 0.7
    )
    answer = executor.execute(query)

    assert answer.result["members"] == []
    assert "does not belong" in answer.explanation


# ---------- ENTITY_SEARCH ----------

def test_entity_search():
    mock_search = Mock()
    mock_search.execute.return_value = [
        mock_node("id-1", "Ravi Kumar", EntityKind.PERSON),
        mock_node("id-2", "Ravi LLC", EntityKind.ORGANIZATION),
    ]

    executor = build_executor(search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.ENTITY_SEARCH, {"name_query": "Ravi"}, 0.95
    )
    answer = executor.execute(query)

    assert answer.intent == QueryIntent.ENTITY_SEARCH
    assert len(answer.result["matches"]) == 2
    assert answer.result["matches"][0]["name"] == "Ravi Kumar"
    assert answer.result["matches"][1]["kind"] == "organization"
    assert "2 entities" in answer.explanation


def test_entity_search_no_results():
    mock_search = Mock()
    mock_search.execute.return_value = []

    executor = build_executor(search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.ENTITY_SEARCH, {"name_query": "nonexistent"}, 0.6
    )
    answer = executor.execute(query)

    assert answer.result["matches"] == []
    assert "0 entities" in answer.explanation


# ---------- GRAPH_SUMMARY ----------

def test_graph_summary():
    mock_stats = Mock()
    mock_stats.execute.return_value = {"total_nodes": 4200, "total_edges": 1800}

    executor = build_executor(stats=mock_stats)
    query = ClassifiedQuery(QueryIntent.GRAPH_SUMMARY, {}, 0.99)
    answer = executor.execute(query)

    assert answer.intent == QueryIntent.GRAPH_SUMMARY
    assert answer.result["total_nodes"] == 4200
    assert answer.result["total_edges"] == 1800
    assert "4200 nodes" in answer.explanation
    assert "1800 edges" in answer.explanation


# ---------- PARAMETER VALIDATION ----------

def test_missing_source_name_raises():
    executor = build_executor()
    query = ClassifiedQuery(
        QueryIntent.SHORTEST_PATH, {"target_name": "bob"}, 0.9
    )
    with pytest.raises(ValidationError, match="source_name"):
        executor.execute(query)


def test_empty_entity_name_raises():
    executor = build_executor()
    query = ClassifiedQuery(
        QueryIntent.NEIGHBORS_WITHIN_HOPS, {"entity_name": "  ", "hops": 1}, 0.9
    )
    with pytest.raises(ValidationError, match="entity_name"):
        executor.execute(query)


def test_missing_name_query_raises():
    executor = build_executor()
    query = ClassifiedQuery(
        QueryIntent.ENTITY_SEARCH, {}, 0.9
    )
    with pytest.raises(ValidationError, match="name_query"):
        executor.execute(query)


# ---------- ENTITY RESOLUTION ----------

def test_resolve_entity_not_found_raises():
    mock_search = Mock()
    mock_search.execute.return_value = []

    executor = build_executor(search=mock_search)
    query = ClassifiedQuery(
        QueryIntent.SHORTEST_PATH,
        {"source_name": "ghost", "target_name": "phantom"},
        0.9,
    )
    with pytest.raises(ValidationError, match="Could not find"):
        executor.execute(query)


def test_unsupported_intent_raises():
    """If somehow a new intent is added without wiring, NotImplementedError raised."""
    executor = build_executor()
    query = ClassifiedQuery.__new__(ClassifiedQuery)
    query.intent = "unknown_intent"
    query.parameters = {}
    query.confidence = 0.5

    # validate_parameters won't find it in REQUIRED_PARAMS but that's OK (defaults to [])
    # execute should fall through to NotImplementedError
    with pytest.raises(NotImplementedError):
        executor.execute(query)

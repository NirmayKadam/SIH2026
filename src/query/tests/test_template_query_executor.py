from unittest.mock import Mock
from query.infrastructure.adapters.template_query_executor import (
    TemplateQueryExecutorAdapter,
)
from query.domain.entities import ClassifiedQuery, QueryIntent
from shared_kernel.domain.value_objects import EntityId, EntityKind
from graph.domain.entities import GraphNode


def _mock_node(id_str, name):
    return GraphNode(
        entity_id=EntityId(id_str),
        kind=EntityKind.PERSON,
        name=name,
        confidence=1.0,
        provenances=[],
    )


def test_executor_shortest_path():
    mock_centrality = Mock()
    mock_shortest = Mock()
    mock_communities = Mock()
    mock_neighborhood = Mock()
    mock_search = Mock()
    mock_stats = Mock()

    # Mock name resolution to return an entity with ID "id-{name}"
    mock_search.execute.side_effect = lambda query, limit: [
        _mock_node(f"id-{query}", query)
    ]

    # Mock shortest path return
    mock_shortest.execute.return_value = Mock(
        found=True, entity_ids=[EntityId("id-a"), EntityId("id-b")]
    )

    executor = TemplateQueryExecutorAdapter(
        mock_centrality,
        mock_shortest,
        mock_communities,
        mock_neighborhood,
        mock_search,
        mock_stats,
    )

    query = ClassifiedQuery(
        QueryIntent.SHORTEST_PATH, {"source_name": "a", "target_name": "b"}, 1.0
    )

    answer = executor.execute(query)

    assert answer.intent == QueryIntent.SHORTEST_PATH
    assert answer.result["found"] is True
    assert answer.result["path"] == ["id-a", "id-b"]

    # Verify that shortest path use case was called with resolved IDs
    mock_shortest.execute.assert_called_once_with(EntityId("id-a"), EntityId("id-b"))

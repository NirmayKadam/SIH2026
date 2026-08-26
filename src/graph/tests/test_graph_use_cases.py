"""Unit tests for Graph bounded context use cases.
All tests mock GraphRepositoryPort — no Neo4j dependency needed."""
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from shared_kernel.domain.value_objects import (
    EntityId, EntityKind, RelationshipKind, Confidence, SourceProvenance, SourceType,
)
from shared_kernel.domain.errors import NotFoundError
from graph.domain.entities import GraphNode, GraphEdge, Neighborhood
from graph.application.use_cases.get_entity_detail import GetEntityDetailUseCase
from graph.application.use_cases.get_entity_neighborhood import GetEntityNeighborhoodUseCase
from graph.application.use_cases.search_entities import SearchEntitiesUseCase
from graph.application.use_cases.get_graph_stats import GetGraphStatsUseCase
from graph.application.use_cases.persist_extraction_result import PersistExtractionResultUseCase
from extraction.domain.entities import ExtractedEntity, ExtractedRelationship


# --- Fixtures ---

SAMPLE_PROVENANCE = SourceProvenance(
    source_type=SourceType.ICIJ_OFFSHORE_LEAKS,
    source_document_id="panama-entity-001",
    ingested_at=datetime(2026, 8, 26, 10, 0, 0),
)

SAMPLE_NODE = GraphNode(
    entity_id=EntityId("icij-001"),
    kind=EntityKind.PERSON,
    name="John Doe",
    confidence=0.92,
    provenances=[SAMPLE_PROVENANCE],
)

SAMPLE_NODE_B = GraphNode(
    entity_id=EntityId("icij-002"),
    kind=EntityKind.ORGANIZATION,
    name="Mossack Fonseca",
    confidence=0.95,
    provenances=[SAMPLE_PROVENANCE],
)

SAMPLE_EDGE = GraphEdge(
    source_entity_id=EntityId("icij-001"),
    target_entity_id=EntityId("icij-002"),
    kind=RelationshipKind.OFFICER_OF,
    confidence=0.88,
    provenances=[SAMPLE_PROVENANCE],
)


def make_mock_repository() -> MagicMock:
    """Create a mock implementing GraphRepositoryPort interface."""
    from graph.application.ports.graph_repository_port import GraphRepositoryPort
    return MagicMock(spec=GraphRepositoryPort)


# --- GetEntityDetailUseCase ---

class TestGetEntityDetail:
    def test_returns_node(self):
        repo = make_mock_repository()
        repo.get_node.return_value = SAMPLE_NODE
        use_case = GetEntityDetailUseCase(repo)

        result = use_case.execute(EntityId("icij-001"))

        assert result == SAMPLE_NODE
        repo.get_node.assert_called_once_with(EntityId("icij-001"))

    def test_not_found_propagates(self):
        repo = make_mock_repository()
        repo.get_node.side_effect = NotFoundError("Entity icij-999 not found")
        use_case = GetEntityDetailUseCase(repo)

        with pytest.raises(NotFoundError, match="icij-999"):
            use_case.execute(EntityId("icij-999"))

    def test_returns_node_with_provenances(self):
        repo = make_mock_repository()
        repo.get_node.return_value = SAMPLE_NODE
        use_case = GetEntityDetailUseCase(repo)

        result = use_case.execute(EntityId("icij-001"))

        assert len(result.provenances) == 1
        assert result.provenances[0].source_type == SourceType.ICIJ_OFFSHORE_LEAKS
        assert result.provenances[0].source_document_id == "panama-entity-001"


# --- SearchEntitiesUseCase ---

class TestSearchEntities:
    def test_delegates_query_and_limit(self):
        repo = make_mock_repository()
        repo.search_nodes.return_value = [SAMPLE_NODE, SAMPLE_NODE_B]
        use_case = SearchEntitiesUseCase(repo)

        result = use_case.execute("Mossack", limit=10)

        assert len(result) == 2
        repo.search_nodes.assert_called_once_with("Mossack", limit=10)

    def test_empty_result_returns_empty_list(self):
        repo = make_mock_repository()
        repo.search_nodes.return_value = []
        use_case = SearchEntitiesUseCase(repo)

        result = use_case.execute("nonexistent", limit=20)

        assert result == []


# --- GetEntityNeighborhoodUseCase ---

class TestGetEntityNeighborhood:
    def test_delegates_with_depth(self):
        repo = make_mock_repository()
        neighborhood = Neighborhood(
            center=SAMPLE_NODE,
            nodes=[SAMPLE_NODE_B],
            edges=[SAMPLE_EDGE],
        )
        repo.get_neighborhood.return_value = neighborhood
        use_case = GetEntityNeighborhoodUseCase(repo)

        result = use_case.execute(EntityId("icij-001"), depth=2)

        assert result.center == SAMPLE_NODE
        assert len(result.nodes) == 1
        assert len(result.edges) == 1
        repo.get_neighborhood.assert_called_once_with(EntityId("icij-001"), depth=2)

    def test_not_found_propagates(self):
        repo = make_mock_repository()
        repo.get_neighborhood.side_effect = NotFoundError("Entity icij-999 not found")
        use_case = GetEntityNeighborhoodUseCase(repo)

        with pytest.raises(NotFoundError, match="icij-999"):
            use_case.execute(EntityId("icij-999"), depth=1)


# --- GetGraphStatsUseCase ---

class TestGetGraphStats:
    def test_returns_dict(self):
        repo = make_mock_repository()
        repo.get_stats.return_value = {"total_nodes": 150, "total_edges": 320}
        use_case = GetGraphStatsUseCase(repo)

        result = use_case.execute()

        assert result == {"total_nodes": 150, "total_edges": 320}
        repo.get_stats.assert_called_once()


# --- PersistExtractionResultUseCase ---

class TestPersistExtractionResult:
    def test_converts_and_upserts(self):
        repo = make_mock_repository()
        use_case = PersistExtractionResultUseCase(repo)

        extracted_entity = ExtractedEntity(
            entity_id=EntityId("icij-001"),
            kind=EntityKind.PERSON,
            name="John Doe",
            confidence=Confidence(0.92),
            provenance=SAMPLE_PROVENANCE,
        )
        extracted_rel = ExtractedRelationship(
            source_entity_id=EntityId("icij-001"),
            target_entity_id=EntityId("icij-002"),
            kind=RelationshipKind.OFFICER_OF,
            confidence=Confidence(0.88),
            provenance=SAMPLE_PROVENANCE,
        )

        use_case.execute([extracted_entity], [extracted_rel])

        assert repo.upsert_node.call_count == 1
        assert repo.upsert_edge.call_count == 1

        # Verify the GraphNode passed to upsert_node
        node_arg = repo.upsert_node.call_args[0][0]
        assert isinstance(node_arg, GraphNode)
        assert node_arg.entity_id == EntityId("icij-001")
        assert node_arg.confidence == 0.92

        # Verify the GraphEdge passed to upsert_edge
        edge_arg = repo.upsert_edge.call_args[0][0]
        assert isinstance(edge_arg, GraphEdge)
        assert edge_arg.source_entity_id == EntityId("icij-001")
        assert edge_arg.target_entity_id == EntityId("icij-002")

    def test_carries_provenance(self):
        repo = make_mock_repository()
        use_case = PersistExtractionResultUseCase(repo)

        extracted_entity = ExtractedEntity(
            entity_id=EntityId("enron-042"),
            kind=EntityKind.PERSON,
            name="Jane Smith",
            confidence=Confidence(0.87),
            provenance=SourceProvenance(
                source_type=SourceType.ENRON_EMAILS,
                source_document_id="enron-msg-67890",
                ingested_at=datetime(2026, 8, 26, 11, 0, 0),
            ),
        )

        use_case.execute([extracted_entity], [])

        node_arg = repo.upsert_node.call_args[0][0]
        assert len(node_arg.provenances) == 1
        assert node_arg.provenances[0].source_type == SourceType.ENRON_EMAILS
        assert node_arg.provenances[0].source_document_id == "enron-msg-67890"

    def test_multiple_entities_and_relationships(self):
        repo = make_mock_repository()
        use_case = PersistExtractionResultUseCase(repo)

        entities = [
            ExtractedEntity(
                entity_id=EntityId(f"entity-{i}"),
                kind=EntityKind.PERSON,
                name=f"Person {i}",
                confidence=Confidence(0.9),
                provenance=SAMPLE_PROVENANCE,
            )
            for i in range(3)
        ]
        relationships = [
            ExtractedRelationship(
                source_entity_id=EntityId("entity-0"),
                target_entity_id=EntityId(f"entity-{i}"),
                kind=RelationshipKind.COMMUNICATED_WITH,
                confidence=Confidence(0.85),
                provenance=SAMPLE_PROVENANCE,
            )
            for i in range(1, 3)
        ]

        use_case.execute(entities, relationships)

        assert repo.upsert_node.call_count == 3
        assert repo.upsert_edge.call_count == 2

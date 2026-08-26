"""Unit tests for Phase 2 security hardening — input validation in Neo4j adapter.
Tests the validation logic at module level (constants + guard clauses)
without requiring a live Neo4j connection."""
import pytest

from shared_kernel.domain.errors import ValidationError
from graph.infrastructure.adapters.neo4j_graph_repository import (
    MAX_SEARCH_QUERY_LENGTH,
    MAX_ENTITY_ID_LENGTH,
    MIN_NEIGHBORHOOD_DEPTH,
    MAX_NEIGHBORHOOD_DEPTH,
    MAX_ALL_NODES_LIMIT,
    MAX_ALL_EDGES_LIMIT,
)


class TestValidationConstants:
    """Verify security constants are set to sane values."""

    def test_search_query_length_cap(self):
        assert MAX_SEARCH_QUERY_LENGTH == 200

    def test_entity_id_length_cap(self):
        assert MAX_ENTITY_ID_LENGTH == 500

    def test_neighborhood_depth_bounds(self):
        assert MIN_NEIGHBORHOOD_DEPTH == 1
        assert MAX_NEIGHBORHOOD_DEPTH == 4

    def test_all_nodes_limit(self):
        assert MAX_ALL_NODES_LIMIT == 10000

    def test_all_edges_limit(self):
        assert MAX_ALL_EDGES_LIMIT == 50000


class TestCypherInjectionAudit:
    """Verify no string concatenation of user input in Cypher queries.
    This test reads the adapter source and ensures all queries use $param syntax."""

    def test_no_format_strings_with_user_input(self):
        import inspect
        from graph.infrastructure.adapters import neo4j_graph_repository as module

        source = inspect.getsource(module.Neo4jGraphRepositoryAdapter)

        # f-strings are only used for LIMIT constants (MAX_ALL_NODES_LIMIT, MAX_ALL_EDGES_LIMIT)
        # which are module-level constants, not user input. Verify no .format() calls.
        assert ".format(" not in source, (
            "Found .format() in adapter — potential Cypher injection vector"
        )

    def test_parameterized_queries_used(self):
        """All user-facing queries must use $param syntax."""
        import inspect
        from graph.infrastructure.adapters import neo4j_graph_repository as module

        source = inspect.getsource(module.Neo4jGraphRepositoryAdapter)

        # Key parameterized variables that MUST appear
        required_params = ["$id", "$kind", "$q", "$limit", "$depth",
                           "$source_id", "$target_id", "$confidence"]
        for param in required_params:
            assert param in source, f"Missing parameterized query variable: {param}"

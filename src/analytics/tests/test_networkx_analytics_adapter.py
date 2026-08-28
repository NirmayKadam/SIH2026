import os
import pytest
from neo4j import GraphDatabase

from analytics.infrastructure.adapters.networkx_analytics_adapter import (
    NetworkxAnalyticsAdapter,
)
from analytics.domain.entities import CentralityType
from shared_kernel.domain.value_objects import EntityId


@pytest.fixture
def analytics_adapter():
    if not os.environ.get("NEO4J_URI"):
        pytest.skip("NEO4J_URI not set")
    return NetworkxAnalyticsAdapter()


@pytest.fixture
def seed_data():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    if not all([uri, user, password]):
        pytest.skip("Neo4j env vars not set")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        # Create a small network: A -> B -> C
        session.run("MATCH (n:Entity) DETACH DELETE n")
        session.run(
            "CREATE (a:Entity {id: 'A', name: 'Alice'})-[:RELATES {confidence: 1.0}]->(b:Entity {id: 'B', name: 'Bob'})-[:RELATES {confidence: 1.0}]->(c:Entity {id: 'C', name: 'Charlie'})"
        )

    yield

    with driver.session() as session:
        session.run("MATCH (n:Entity) DETACH DELETE n")
    driver.close()


def test_compute_centrality(analytics_adapter, seed_data):
    scores = analytics_adapter.compute_centrality(CentralityType.DEGREE)
    assert len(scores) == 3
    # B is in the middle, so it should have the highest degree centrality
    score_map = {s.entity_id.value: s.score for s in scores}
    assert score_map["B"] > score_map["A"]
    assert score_map["B"] > score_map["C"]


def test_detect_communities(analytics_adapter, seed_data):
    communities = analytics_adapter.detect_communities()
    assert len(communities) > 0


def test_shortest_path(analytics_adapter, seed_data):
    path = analytics_adapter.shortest_path(EntityId("A"), EntityId("C"))
    assert path.found is True
    assert len(path.entity_ids) == 3
    assert path.entity_ids[0].value == "A"
    assert path.entity_ids[-1].value == "C"


def test_shortest_path_not_found(analytics_adapter, seed_data):
    path = analytics_adapter.shortest_path(EntityId("A"), EntityId("Z"))
    assert path.found is False
    assert len(path.entity_ids) == 0

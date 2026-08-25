"""
Real Neo4j Community Edition adapter — working skeleton using the official driver.
Requires NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD (see .env.example). Fails fast if
the connection can't be established — no in-memory fallback pretending to be Neo4j.
"""
import os

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import GraphNode, GraphEdge, Neighborhood
from shared_kernel.domain.value_objects import EntityId
from shared_kernel.domain.errors import ExternalServiceError, NotFoundError


class Neo4jGraphRepositoryAdapter(GraphRepositoryPort):
    def __init__(self) -> None:
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        if not all([uri, user, password]):
            raise ExternalServiceError(
                "NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD must all be set — "
                "refusing to start without a real graph database."
            )
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
        except Exception as exc:
            raise ExternalServiceError(f"Could not connect to Neo4j at {uri}: {exc}") from exc

    def upsert_node(self, node: GraphNode) -> None:
        query = """
        MERGE (n:Entity {id: $id})
        SET n.kind = $kind, n.name = $name, n.confidence = $confidence
        """
        try:
            with self._driver.session() as session:
                session.run(
                    query, id=node.entity_id.value, kind=node.kind.value,
                    name=node.name, confidence=node.confidence,
                )
        except Neo4jError as exc:
            raise ExternalServiceError(f"Failed to upsert node {node.entity_id.value}: {exc}") from exc

    def upsert_edge(self, edge: GraphEdge) -> None:
        query = """
        MATCH (a:Entity {id: $source_id}), (b:Entity {id: $target_id})
        MERGE (a)-[r:RELATES {kind: $kind}]->(b)
        SET r.confidence = $confidence
        """
        try:
            with self._driver.session() as session:
                session.run(
                    query,
                    source_id=edge.source_entity_id.value,
                    target_id=edge.target_entity_id.value,
                    kind=edge.kind.value,
                    confidence=edge.confidence,
                )
        except Neo4jError as exc:
            raise ExternalServiceError(f"Failed to upsert edge: {exc}") from exc

    def get_neighborhood(self, entity_id: EntityId, depth: int = 1) -> Neighborhood:
        # NOT YET IMPLEMENTED: real Cypher variable-length path query + mapping back
        # to GraphNode/GraphEdge/Neighborhood domain objects. Build against a real
        # loaded graph, not a hand-typed fixture.
        raise NotImplementedError(
            "Implement variable-length neighborhood query, e.g. "
            "MATCH (center:Entity {id: $id})-[r*1..$depth]-(n) RETURN center, r, n"
        )

    def close(self) -> None:
        self._driver.close()

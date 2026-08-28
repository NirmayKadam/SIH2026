"""
Real Neo4j Community Edition adapter — uses the official driver.
Requires NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD (see .env.example). Fails fast if
the connection can't be established — no in-memory fallback pretending to be Neo4j.
"""
import json
import os
from datetime import datetime

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import GraphNode, GraphEdge, Neighborhood
from shared_kernel.domain.value_objects import (
    EntityId, EntityKind, RelationshipKind, SourceProvenance, SourceType,
)
from shared_kernel.domain.errors import (
    ExternalServiceError, NotFoundError, ValidationError,
)

# --- Constants for input validation (Phase 2 security hardening) ---
MAX_SEARCH_QUERY_LENGTH = 200
MAX_ENTITY_ID_LENGTH = 500
MIN_NEIGHBORHOOD_DEPTH = 1
MAX_NEIGHBORHOOD_DEPTH = 4
MAX_ALL_NODES_LIMIT = 10000
MAX_ALL_EDGES_LIMIT = 50000


def serialize_provenances(provenances: list[SourceProvenance]) -> str:
    """Convert list of SourceProvenance to JSON string for Neo4j storage.
    Neo4j Community Edition doesn't support nested maps in lists natively."""
    return json.dumps([
        {
            "source_type": p.source_type.value,
            "source_document_id": p.source_document_id,
            "ingested_at": p.ingested_at.isoformat(),
        }
        for p in provenances
    ])


def deserialize_provenances(json_str: str | None) -> list[SourceProvenance]:
    """Convert JSON string from Neo4j back to list of SourceProvenance."""
    if not json_str:
        return []
    raw_list = json.loads(json_str)
    return [
        SourceProvenance(
            source_type=SourceType(item["source_type"]),
            source_document_id=item["source_document_id"],
            ingested_at=datetime.fromisoformat(item["ingested_at"]),
        )
        for item in raw_list
    ]


def merge_provenances(
    existing_json: str | None, new_provenances: list[SourceProvenance]
) -> str:
    """Append new provenances to existing, deduplicate by source_document_id."""
    existing = deserialize_provenances(existing_json)
    seen_doc_ids = {p.source_document_id for p in existing}
    for p in new_provenances:
        if p.source_document_id not in seen_doc_ids:
            existing.append(p)
            seen_doc_ids.add(p.source_document_id)
    return serialize_provenances(existing)


def record_to_node(record) -> GraphNode:
    """Map a Neo4j record (with node properties) to a GraphNode domain object."""
    node = record["n"]
    return GraphNode(
        entity_id=EntityId(node["id"]),
        kind=EntityKind(node["kind"]),
        name=node["name"],
        confidence=node["confidence"],
        provenances=deserialize_provenances(node.get("provenances")),
    )


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
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
        except Exception as exc:
            raise ExternalServiceError(f"Could not connect to Neo4j at {uri}: {exc}") from exc

    def upsert_node(self, node: GraphNode) -> None:
        """MERGE node by id, append provenances (deduplicate by source_document_id)."""
        read_query = "MATCH (n:Entity {id: $id}) RETURN n.provenances AS existing_prov"
        write_query = """
        MERGE (n:Entity {id: $id})
        SET n.kind = $kind, n.name = $name, n.confidence = $confidence,
            n.provenances = $provenances_json
        """
        try:
            with self.driver.session() as session:
                result = session.run(read_query, id=node.entity_id.value)
                record = result.single()
                existing_json = record["existing_prov"] if record else None
                merged_json = merge_provenances(existing_json, node.provenances)

                session.run(
                    write_query,
                    id=node.entity_id.value,
                    kind=node.kind.value,
                    name=node.name,
                    confidence=node.confidence,
                    provenances_json=merged_json,
                )
        except Neo4jError as exc:
            raise ExternalServiceError(
                f"Failed to upsert node {node.entity_id.value}: {exc}"
            ) from exc

    def upsert_edge(self, edge: GraphEdge) -> None:
        """MERGE edge by source+target+kind, append provenances."""
        read_query = """
        MATCH (a:Entity {id: $source_id})-[r:RELATES {kind: $kind}]->(b:Entity {id: $target_id})
        RETURN r.provenances AS existing_prov
        """
        write_query = """
        MATCH (a:Entity {id: $source_id}), (b:Entity {id: $target_id})
        MERGE (a)-[r:RELATES {kind: $kind}]->(b)
        SET r.confidence = $confidence, r.provenances = $provenances_json
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    read_query,
                    source_id=edge.source_entity_id.value,
                    target_id=edge.target_entity_id.value,
                    kind=edge.kind.value,
                )
                record = result.single()
                existing_json = record["existing_prov"] if record else None
                merged_json = merge_provenances(existing_json, edge.provenances)

                session.run(
                    write_query,
                    source_id=edge.source_entity_id.value,
                    target_id=edge.target_entity_id.value,
                    kind=edge.kind.value,
                    confidence=edge.confidence,
                    provenances_json=merged_json,
                )
        except Neo4jError as exc:
            raise ExternalServiceError(f"Failed to upsert edge: {exc}") from exc

    def get_node(self, entity_id: EntityId) -> GraphNode:
        """Retrieve a single node by EntityId. Raises NotFoundError if not in graph.
        SECURITY: Cypher injection safe — uses parameterized $id."""
        if len(entity_id.value) > MAX_ENTITY_ID_LENGTH:
            raise ValidationError(
                f"Entity ID exceeds maximum length of {MAX_ENTITY_ID_LENGTH} characters"
            )
        query = "MATCH (n:Entity {id: $id}) RETURN n"
        try:
            with self.driver.session() as session:
                result = session.run(query, id=entity_id.value)
                record = result.single()
                if record is None:
                    raise NotFoundError(f"Entity {entity_id.value} not found in graph")
                return record_to_node(record)
        except NotFoundError:
            raise
        except Neo4jError as exc:
            raise ExternalServiceError(
                f"Failed to get node {entity_id.value}: {exc}"
            ) from exc

    def search_nodes(self, name_query: str, limit: int = 20) -> list[GraphNode]:
        """Case-insensitive name search. Returns up to `limit` matching nodes.
        SECURITY: Cypher injection safe — uses parameterized $q and $limit."""
        if not name_query or not name_query.strip():
            return []
        if len(name_query) > MAX_SEARCH_QUERY_LENGTH:
            raise ValidationError(
                f"Search query exceeds maximum length of {MAX_SEARCH_QUERY_LENGTH} characters"
            )
        query = """
        MATCH (n:Entity)
        WHERE toLower(n.name) CONTAINS toLower($q)
        RETURN n
        LIMIT $limit
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, q=name_query.strip(), limit=limit)
                return [record_to_node(record) for record in result]
        except Neo4jError as exc:
            raise ExternalServiceError(
                f"Failed to search nodes with query '{name_query}': {exc}"
            ) from exc

    def get_neighborhood(self, entity_id: EntityId, depth: int = 1) -> Neighborhood:
        """Retrieve N-hop neighborhood around an entity. Raises NotFoundError if
        center node doesn't exist.
        SECURITY: Cypher injection safe — uses parameterized $id and $depth.
        Defense-in-depth: depth validated here even though REST layer caps it."""
        if not (MIN_NEIGHBORHOOD_DEPTH <= depth <= MAX_NEIGHBORHOOD_DEPTH):
            raise ValidationError(
                f"Neighborhood depth must be between {MIN_NEIGHBORHOOD_DEPTH} and "
                f"{MAX_NEIGHBORHOOD_DEPTH}, got {depth}"
            )
        center = self.get_node(entity_id)

        path_query = f"""
        MATCH p = (center:Entity {{id: $id}})-[*1..{depth}]-(neighbor)
        WHERE neighbor:Entity
        RETURN nodes(p) AS path_nodes, relationships(p) AS path_rels
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    path_query, id=entity_id.value
                )

                seen_node_ids: set[str] = {entity_id.value}
                neighbor_nodes: list[GraphNode] = []
                seen_edge_keys: set[tuple] = set()
                edges: list[GraphEdge] = []

                for record in result:
                    for neo_node in record["path_nodes"]:
                        node_id = neo_node["id"]
                        if node_id not in seen_node_ids:
                            seen_node_ids.add(node_id)
                            neighbor_nodes.append(GraphNode(
                                entity_id=EntityId(node_id),
                                kind=EntityKind(neo_node["kind"]),
                                name=neo_node["name"],
                                confidence=neo_node["confidence"],
                                provenances=deserialize_provenances(
                                    neo_node.get("provenances")
                                ),
                            ))

                    for neo_rel in record["path_rels"]:
                        start_id = neo_rel.start_node["id"]
                        end_id = neo_rel.end_node["id"]
                        rel_kind = neo_rel["kind"]
                        edge_key = (start_id, end_id, rel_kind)
                        if edge_key not in seen_edge_keys:
                            seen_edge_keys.add(edge_key)
                            edges.append(GraphEdge(
                                source_entity_id=EntityId(start_id),
                                target_entity_id=EntityId(end_id),
                                kind=RelationshipKind(rel_kind),
                                confidence=neo_rel["confidence"],
                                provenances=deserialize_provenances(
                                    neo_rel.get("provenances")
                                ),
                            ))

                return Neighborhood(
                    center=center,
                    nodes=neighbor_nodes,
                    edges=edges,
                )
        except NotFoundError:
            raise
        except Neo4jError as exc:
            raise ExternalServiceError(
                f"Failed to get neighborhood for {entity_id.value}: {exc}"
            ) from exc

    def get_all_nodes(self) -> list[GraphNode]:
        """Return every node in the graph. Used by Analytics (NetworkX) to build
        in-memory graph for algorithm execution.
        SECURITY: Capped at MAX_ALL_NODES_LIMIT to prevent OOM on large graphs.
        Cypher injection safe — no user input in query."""
        query = f"MATCH (n:Entity) RETURN n LIMIT {MAX_ALL_NODES_LIMIT}"
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [record_to_node(record) for record in result]
        except Neo4jError as exc:
            raise ExternalServiceError(f"Failed to get all nodes: {exc}") from exc

    def get_all_edges(self) -> list[GraphEdge]:
        """Return every edge in the graph. Used alongside get_all_nodes by Analytics.
        SECURITY: Capped at MAX_ALL_EDGES_LIMIT to prevent OOM.
        Cypher injection safe — no user input in query."""
        query = f"""
        MATCH (a:Entity)-[r:RELATES]->(b:Entity)
        RETURN a.id AS source, b.id AS target,
               r.kind AS kind, r.confidence AS confidence,
               r.provenances AS provenances
        LIMIT {MAX_ALL_EDGES_LIMIT}
        """
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [
                    GraphEdge(
                        source_entity_id=EntityId(record["source"]),
                        target_entity_id=EntityId(record["target"]),
                        kind=RelationshipKind(record["kind"]),
                        confidence=record["confidence"],
                        provenances=deserialize_provenances(record["provenances"]),
                    )
                    for record in result
                ]
        except Neo4jError as exc:
            raise ExternalServiceError(f"Failed to get all edges: {exc}") from exc

    def get_stats(self) -> dict:
        """Return {'total_nodes': int, 'total_edges': int}."""
        node_query = "MATCH (n:Entity) RETURN count(n) AS total_nodes"
        edge_query = "MATCH ()-[r]->() RETURN count(r) AS total_edges"
        try:
            with self.driver.session() as session:
                node_result = session.run(node_query).single()
                edge_result = session.run(edge_query).single()
                return {
                    "total_nodes": node_result["total_nodes"],
                    "total_edges": edge_result["total_edges"],
                }
        except Neo4jError as exc:
            raise ExternalServiceError(f"Failed to get stats: {exc}") from exc

    def close(self) -> None:
        self.driver.close()

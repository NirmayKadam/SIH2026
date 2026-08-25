"""
NetworkX-based analytics adapter. This is the SAFE DEFAULT (see ARCHITECTURE.md #3 and
the confirmed Neo4j Community Edition decision): rather than depend on Neo4j GDS library
algorithm availability (some centrality/community variants are Enterprise-only depending
on GDS edition), this adapter pulls the current graph out of Neo4j via a Cypher read,
builds an in-memory NetworkX graph, and runs algorithms there. Free, no licensing
questions, and networkx.algorithms has Louvain (via networkx.algorithms.community),
betweenness/degree/pagerank centrality, and shortest_path built in.

Requires a live Neo4j connection to read the graph — no synthetic/hand-built graph.
"""
import os

import networkx as nx
from neo4j import GraphDatabase

from analytics.application.ports.graph_analytics_port import GraphAnalyticsPort
from analytics.domain.entities import CentralityScore, Community, PathResult, CentralityType
from shared_kernel.domain.value_objects import EntityId
from shared_kernel.domain.errors import ExternalServiceError


class NetworkxAnalyticsAdapter(GraphAnalyticsPort):
    def __init__(self) -> None:
        uri = os.environ.get("NEO4J_URI")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASSWORD")
        if not all([uri, user, password]):
            raise ExternalServiceError("NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD must be set")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def _load_graph(self) -> nx.Graph:
        query = """
        MATCH (a:Entity)-[r:RELATES]->(b:Entity)
        RETURN a.id AS source, b.id AS target, r.confidence AS confidence
        """
        graph = nx.Graph()
        try:
            with self._driver.session() as session:
                for record in session.run(query):
                    graph.add_edge(record["source"], record["target"], weight=record["confidence"])
        except Exception as exc:
            raise ExternalServiceError(f"Failed to load graph from Neo4j for analytics: {exc}") from exc
        return graph

    def compute_centrality(self, centrality_type: CentralityType) -> list[CentralityScore]:
        graph = self._load_graph()
        if centrality_type == CentralityType.DEGREE:
            scores = nx.degree_centrality(graph)
        elif centrality_type == CentralityType.BETWEENNESS:
            scores = nx.betweenness_centrality(graph)
        elif centrality_type == CentralityType.PAGERANK:
            scores = nx.pagerank(graph)
        else:
            raise ValueError(f"Unsupported centrality type: {centrality_type}")
        return [CentralityScore(entity_id=EntityId(k), score=v) for k, v in scores.items()]

    def detect_communities(self) -> list[Community]:
        graph = self._load_graph()
        from networkx.algorithms.community import louvain_communities
        raw_communities = louvain_communities(graph, weight="weight")
        return [
            Community(community_id=i, member_entity_ids=[EntityId(n) for n in community])
            for i, community in enumerate(raw_communities)
        ]

    def shortest_path(self, source: EntityId, target: EntityId) -> PathResult:
        graph = self._load_graph()
        try:
            path = nx.shortest_path(graph, source=source.value, target=target.value)
            return PathResult(found=True, entity_ids=[EntityId(n) for n in path])
        except nx.NetworkXNoPath:
            return PathResult(found=False, entity_ids=[])
        except nx.NodeNotFound:
            return PathResult(found=False, entity_ids=[])

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
from analytics.domain.entities import (
    CentralityScore, Community, PathResult, CentralityType,
    SuspiciousPattern, PatternType,
)
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

    def _load_digraph(self) -> nx.DiGraph:
        """Load a directed graph for cycle detection and flow analysis."""
        query = """
        MATCH (a:Entity)-[r:RELATES]->(b:Entity)
        RETURN a.id AS source, b.id AS target, r.kind AS kind, r.confidence AS confidence
        """
        graph = nx.DiGraph()
        try:
            with self._driver.session() as session:
                for record in session.run(query):
                    graph.add_edge(
                        record["source"], record["target"],
                        kind=record["kind"], weight=record["confidence"],
                    )
        except Exception as exc:
            raise ExternalServiceError(f"Failed to load digraph from Neo4j: {exc}") from exc
        return graph

    def _load_node_kinds(self) -> dict[str, str]:
        """Load entity_id -> kind mapping from Neo4j for pattern analysis."""
        query = "MATCH (n:Entity) RETURN n.id AS id, n.kind AS kind, n.name AS name"
        mapping: dict[str, str] = {}
        try:
            with self._driver.session() as session:
                for record in session.run(query):
                    mapping[record["id"]] = record["kind"]
        except Exception as exc:
            raise ExternalServiceError(f"Failed to load node kinds: {exc}") from exc
        return mapping

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

    def detect_suspicious_patterns(self) -> list[SuspiciousPattern]:
        """Run all anomaly detection algorithms against the live graph.

        Detection strategies:
        1. High-Betweenness Facilitators — nodes that bridge otherwise disconnected
           clusters. In criminal networks, these are often intermediaries or fixers.
        2. Shell Company Clusters — organizations connected to a disproportionate
           number of other entities through a single intermediary (star topology).
        3. Circular Flows — directed cycles suggesting money laundering loops.
        """
        patterns: list[SuspiciousPattern] = []
        graph = self._load_graph()

        if graph.number_of_nodes() == 0:
            return patterns

        # --- 1. High-Betweenness Facilitators ---
        betweenness = nx.betweenness_centrality(graph)
        degree = nx.degree_centrality(graph)
        node_kinds = self._load_node_kinds()

        if betweenness:
            scores = sorted(betweenness.values(), reverse=True)
            # Dynamic threshold: top 5% or mean + 2*std, whichever is more selective
            import statistics
            if len(scores) >= 5:
                mean_b = statistics.mean(scores)
                std_b = statistics.stdev(scores)
                stat_threshold = mean_b + 2 * std_b
                percentile_threshold = scores[max(1, len(scores) // 20) - 1]
                threshold = max(stat_threshold, percentile_threshold)
            else:
                threshold = 0.3

            for node_id, b_score in betweenness.items():
                d_score = degree.get(node_id, 0)
                # High betweenness but relatively low degree = broker/facilitator
                if b_score >= threshold and d_score < 0.5:
                    kind = node_kinds.get(node_id, "unknown")
                    patterns.append(SuspiciousPattern(
                        pattern_type=PatternType.HIGH_BETWEENNESS_FACILITATOR,
                        description=(
                            f"Entity '{node_id}' (type: {kind}) acts as a critical bridge "
                            f"between otherwise disconnected clusters. "
                            f"Betweenness: {b_score:.4f}, Degree: {d_score:.4f}."
                        ),
                        involved_entity_ids=[EntityId(node_id)],
                        risk_score=min(1.0, b_score * 2),
                        details={
                            "betweenness_centrality": f"{b_score:.6f}",
                            "degree_centrality": f"{d_score:.6f}",
                            "entity_kind": kind,
                        },
                    ))

        # --- 2. Shell Company Clusters (star topology detection) ---
        # Find nodes that act as hubs connecting many leaf nodes (degree-1 neighbors)
        for node_id in graph.nodes():
            neighbors = list(graph.neighbors(node_id))
            if len(neighbors) < 5:
                continue

            leaf_neighbors = [n for n in neighbors if graph.degree(n) == 1]
            leaf_ratio = len(leaf_neighbors) / len(neighbors)

            if leaf_ratio >= 0.6 and len(leaf_neighbors) >= 3:
                hub_kind = node_kinds.get(node_id, "unknown")
                involved = [EntityId(node_id)] + [EntityId(ln) for ln in leaf_neighbors[:10]]
                patterns.append(SuspiciousPattern(
                    pattern_type=PatternType.SHELL_COMPANY_CLUSTER,
                    description=(
                        f"Entity '{node_id}' (type: {hub_kind}) connects to "
                        f"{len(leaf_neighbors)} isolated entities out of "
                        f"{len(neighbors)} total connections ({leaf_ratio:.0%} leaf ratio). "
                        f"This star topology is characteristic of shell company networks."
                    ),
                    involved_entity_ids=involved,
                    risk_score=min(1.0, leaf_ratio * (len(leaf_neighbors) / 10)),
                    details={
                        "total_connections": str(len(neighbors)),
                        "leaf_connections": str(len(leaf_neighbors)),
                        "leaf_ratio": f"{leaf_ratio:.2%}",
                        "hub_kind": hub_kind,
                    },
                ))

        # --- 3. Circular Flow Detection ---
        digraph = self._load_digraph()
        if digraph.number_of_nodes() > 0:
            try:
                # Limit cycle length to avoid combinatorial explosion
                cycles_found = 0
                for cycle in nx.simple_cycles(digraph, length_bound=5):
                    if len(cycle) >= 3:
                        cycle_ids = [EntityId(n) for n in cycle]
                        patterns.append(SuspiciousPattern(
                            pattern_type=PatternType.CIRCULAR_FLOW,
                            description=(
                                f"Circular connection detected among {len(cycle)} entities: "
                                f"{' → '.join(cycle[:5])}{'…' if len(cycle) > 5 else ''} → (back to start). "
                                f"Circular flows can indicate money laundering or layering schemes."
                            ),
                            involved_entity_ids=cycle_ids,
                            risk_score=min(1.0, 0.5 + (len(cycle) * 0.1)),
                            details={
                                "cycle_length": str(len(cycle)),
                                "cycle_path": " → ".join(cycle),
                            },
                        ))
                        cycles_found += 1
                        if cycles_found >= 20:
                            break
            except Exception:
                pass  # Graph may be too large for cycle enumeration — degrade gracefully

        # Sort by risk score descending
        patterns.sort(key=lambda p: p.risk_score, reverse=True)
        return patterns


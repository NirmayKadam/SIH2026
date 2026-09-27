"""Query domain — pure Python. Deliberately scoped to a FIXED set of intents
(see ARCHITECTURE.md critic note #1) rather than open-ended Cypher generation."""
from dataclasses import dataclass
from enum import Enum


class QueryIntent(str, Enum):
    SHORTEST_PATH = "shortest_path"
    TOP_CENTRAL_NODES = "top_central_nodes"
    NEIGHBORS_WITHIN_HOPS = "neighbors_within_hops"
    COMMUNITY_MEMBERS = "community_members"
    ENTITY_SEARCH = "entity_search"
    GRAPH_SUMMARY = "graph_summary"
    TEMPORAL_FILTER = "temporal_filter"
    FIND_NEARBY = "find_nearby"


@dataclass
class ClassifiedQuery:
    intent: QueryIntent
    parameters: dict  # e.g. {"source_name": "...", "target_name": "..."} — genuinely extracted, not templated defaults
    confidence: float


@dataclass
class QueryAnswer:
    intent: QueryIntent
    result: dict
    explanation: str  # human-readable, built from the real result — never a canned sentence

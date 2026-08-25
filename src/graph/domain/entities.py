"""Graph domain — pure Python."""
from dataclasses import dataclass
from shared_kernel.domain.value_objects import EntityId, EntityKind, RelationshipKind


@dataclass
class GraphNode:
    entity_id: EntityId
    kind: EntityKind
    name: str
    confidence: float


@dataclass
class GraphEdge:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind
    confidence: float


@dataclass
class Neighborhood:
    center: GraphNode
    nodes: list[GraphNode]
    edges: list[GraphEdge]

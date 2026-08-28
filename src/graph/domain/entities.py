"""Graph domain — pure Python."""
from dataclasses import dataclass, field
from shared_kernel.domain.value_objects import (
    EntityId, EntityKind, RelationshipKind, SourceProvenance,
)


@dataclass
class GraphNode:
    entity_id: EntityId
    kind: EntityKind
    name: str
    confidence: float
    provenances: list[SourceProvenance] = field(default_factory=list)
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind
    confidence: float
    provenances: list[SourceProvenance] = field(default_factory=list)
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class Neighborhood:
    center: GraphNode
    nodes: list[GraphNode]
    edges: list[GraphEdge]

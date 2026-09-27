"""Graph domain — pure Python."""
from dataclasses import dataclass, field
from datetime import datetime
from shared_kernel.domain.value_objects import (
    EntityId, EntityKind, RelationshipKind, SourceProvenance, GeoPoint
)


@dataclass
class GraphNode:
    entity_id: EntityId
    kind: EntityKind
    name: str
    confidence: float
    provenances: list[SourceProvenance] = field(default_factory=list)
    geo_point: GeoPoint | None = None
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind
    confidence: float
    provenances: list[SourceProvenance] = field(default_factory=list)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class Neighborhood:
    center: GraphNode
    nodes: list[GraphNode]
    edges: list[GraphEdge]

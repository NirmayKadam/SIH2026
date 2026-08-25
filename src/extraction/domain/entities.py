"""Extraction domain — pure Python."""
from dataclasses import dataclass
from shared_kernel.domain.value_objects import (
    EntityId, Confidence, SourceProvenance, SourceType, EntityKind, RelationshipKind,
)


@dataclass
class DocumentInput:
    """What Extraction needs to do its job. Mapped from Ingestion's RawDocument
    at the worker boundary — Extraction never imports ingestion.domain."""
    document_id: str
    source_type: SourceType
    raw_text: str


@dataclass
class ExtractedEntity:
    entity_id: EntityId
    kind: EntityKind
    name: str
    confidence: Confidence
    provenance: SourceProvenance


@dataclass
class ExtractedRelationship:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind
    confidence: Confidence
    provenance: SourceProvenance


@dataclass
class ResolutionCandidate:
    """Two entities that might be the same real-world identity (alias resolution)."""
    entity_a: EntityId
    entity_b: EntityId
    similarity_score: float  # genuinely computed (e.g. rapidfuzz ratio), never hardcoded

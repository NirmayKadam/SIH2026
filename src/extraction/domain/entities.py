"""Extraction domain — pure Python."""
from dataclasses import dataclass
from enum import Enum
from shared_kernel.domain.value_objects import EntityId, Confidence, SourceProvenance


class EntityKind(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    ACCOUNT = "account"
    LOCATION = "location"
    EVENT = "event"


class RelationshipKind(str, Enum):
    COMMUNICATED_WITH = "communicated_with"
    TRANSACTED_WITH = "transacted_with"
    OFFICER_OF = "officer_of"
    INTERMEDIARY_OF = "intermediary_of"
    PRESENT_AT = "present_at"
    MENTIONED_WITH = "mentioned_with"


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

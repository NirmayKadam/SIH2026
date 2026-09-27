"""
Shared value objects used across every bounded context.
These are pure Python — no framework, no I/O, no external dependencies.
"""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class EntityKind(str, Enum):
    """Type of real-world entity extracted from source data."""
    PERSON = "person"
    ORGANIZATION = "organization"
    ACCOUNT = "account"
    LOCATION = "location"
    EVENT = "event"
    VEHICLE = "vehicle"
    PHONE_NUMBER = "phone_number"


class RelationshipKind(str, Enum):
    """Type of relationship between entities, derived from real data patterns."""
    COMMUNICATED_WITH = "communicated_with"
    TRANSACTED_WITH = "transacted_with"
    OFFICER_OF = "officer_of"
    INTERMEDIARY_OF = "intermediary_of"
    PRESENT_AT = "present_at"
    MENTIONED_WITH = "mentioned_with"
    REGISTERED_AT = "registered_at"
    SAME_AS = "same_as"
    OWNS_VEHICLE = "owns_vehicle"
    CALLED = "called"
    FUNDED_BY = "funded_by"


@dataclass(frozen=True)
class EntityId:
    """Identifies a real-world entity (person, org, account, location, event) across contexts."""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("EntityId cannot be empty")


@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")


class SourceType(str, Enum):
    """Which real dataset a piece of data originated from. No 'SYNTHETIC' value exists on purpose."""
    ICIJ_OFFSHORE_LEAKS = "icij_offshore_leaks"
    ENRON_EMAILS = "enron_emails"
    COURT_JUDGMENT = "court_judgment"


@dataclass(frozen=True)
class EvidenceHash:
    """A cryptographic hash representing the immutable proof of a source document."""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("EvidenceHash cannot be empty")


@dataclass(frozen=True)
class SourceProvenance:
    """
    Tracks exactly where a piece of extracted data came from.
    Rule: every entity/relationship written to the graph MUST carry provenance.
    No node or edge may exist without a traceable real source.
    """
    source_type: SourceType
    source_document_id: str
    ingested_at: datetime
    evidence_hash: EvidenceHash | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


@dataclass(frozen=True)
class Confidence:
    """
    A genuinely computed confidence score (0.0-1.0), e.g. from an extraction model's
    own output or a similarity metric. Never hardcode this value — see ARCHITECTURE.md rule 4.
    """
    score: float

    def __post_init__(self):
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.score}")

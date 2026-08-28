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


@dataclass(frozen=True)
class EntityId:
    """Identifies a real-world entity (person, org, account, location, event) across contexts."""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("EntityId cannot be empty")


class SourceType(str, Enum):
    """Which real dataset a piece of data originated from. No 'SYNTHETIC' value exists on purpose."""
    ICIJ_OFFSHORE_LEAKS = "icij_offshore_leaks"
    ENRON_EMAILS = "enron_emails"
    COURT_JUDGMENT = "court_judgment"


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

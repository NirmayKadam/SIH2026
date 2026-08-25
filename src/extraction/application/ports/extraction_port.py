from abc import ABC, abstractmethod
from ingestion.domain.entities import RawDocument
from extraction.domain.entities import ExtractedEntity, ExtractedRelationship


class EntityExtractionPort(ABC):
    """Implemented by the LLM adapter. Must raise ExternalServiceError (or
    RateLimitExceededError) on failure — never return an empty list to mask a failed call."""

    @abstractmethod
    def extract(self, document: RawDocument) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
        ...

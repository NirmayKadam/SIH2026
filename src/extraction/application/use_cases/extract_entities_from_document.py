from ingestion.domain.entities import RawDocument
from extraction.application.ports.extraction_port import EntityExtractionPort
from extraction.application.ports.identity_resolution_port import IdentityResolutionPort
from extraction.domain.entities import ExtractedEntity, ExtractedRelationship, ResolutionCandidate


class ExtractEntitiesFromDocumentUseCase:
    """Orchestrates: raw document -> LLM extraction -> identity resolution candidates.
    Persisting to the graph is a separate concern, handled by the Graph context
    (this use case returns extraction results; the worker wires the handoff)."""

    def __init__(
        self,
        extractor: EntityExtractionPort,
        resolver: IdentityResolutionPort,
    ) -> None:
        self._extractor = extractor
        self._resolver = resolver

    def execute(
        self, document: RawDocument
    ) -> tuple[list[ExtractedEntity], list[ExtractedRelationship], list[ResolutionCandidate]]:
        entities, relationships = self._extractor.extract(document)
        candidates = self._resolver.find_candidates(entities)
        return entities, relationships, candidates

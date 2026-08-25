"""
Real unit test against real logic — no mocking of the thing under test.
This is the pattern: pure-logic adapters (no external service) get real tests,
adapters that call Neo4j/Gemini get integration tests run against real (even if
subsampled) data/services instead of mocks — see ARCHITECTURE.md rule 1.
"""
from datetime import datetime

from extraction.infrastructure.adapters.rapidfuzz_identity_resolver import (
    RapidFuzzIdentityResolutionAdapter,
)
from extraction.domain.entities import ExtractedEntity, EntityKind
from shared_kernel.domain.value_objects import EntityId, Confidence, SourceProvenance, SourceType


def _entity(name: str, entity_id: str) -> ExtractedEntity:
    return ExtractedEntity(
        entity_id=EntityId(entity_id),
        kind=EntityKind.PERSON,
        name=name,
        confidence=Confidence(0.9),
        provenance=SourceProvenance(
            source_type=SourceType.COURT_JUDGMENT,
            source_document_id="test-doc",
            ingested_at=datetime.utcnow(),
        ),
    )


def test_finds_likely_alias_pair():
    resolver = RapidFuzzIdentityResolutionAdapter()
    entities = [_entity("Ravi Kumar", "e1"), _entity("Ravi  Kumar", "e2")]

    candidates = resolver.find_candidates(entities)

    assert len(candidates) == 1
    assert candidates[0].similarity_score > 0.9


def test_does_not_match_clearly_different_names():
    resolver = RapidFuzzIdentityResolutionAdapter()
    entities = [_entity("Ravi Kumar", "e1"), _entity("Suresh Patel", "e2")]

    candidates = resolver.find_candidates(entities)

    assert candidates == []

import os
import pytest

from extraction.infrastructure.adapters.gemini_entity_extractor import (
    GeminiEntityExtractionAdapter,
)
from extraction.domain.entities import DocumentInput
from shared_kernel.domain.value_objects import SourceType


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY required"
)
def test_extract_entities_real_api_call():
    extractor = GeminiEntityExtractionAdapter()

    doc = DocumentInput(
        document_id="test-doc-id",
        source_type=SourceType.COURT_JUDGMENT,
        raw_text="""
        On 12-05-2023, Ravi Kumar was present at Delhi High Court. He communicated with his lawyer, Suresh Patel.
        """,
    )

    entities, relationships = extractor.extract(doc)

    assert len(entities) > 0
    # Check that it extracted the key people
    names = [e.name.lower() for e in entities]
    assert any("ravi" in name for name in names)
    assert any("suresh" in name for name in names)

    # Assert they have proper types, Confidences, and SourceProvenance
    for e in entities:
        assert e.entity_id.value
        assert 0.0 <= e.confidence.score <= 1.0
        assert e.provenance.source_document_id == "test-doc-id"
        assert e.provenance.source_type == SourceType.COURT_JUDGMENT

    # Check relationships
    if relationships:
        for r in relationships:
            assert r.source_entity_id.value
            assert r.target_entity_id.value
            assert 0.0 <= r.confidence.score <= 1.0
            assert r.provenance.source_document_id == "test-doc-id"

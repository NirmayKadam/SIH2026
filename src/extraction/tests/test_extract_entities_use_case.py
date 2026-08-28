from unittest.mock import Mock
from datetime import datetime

from extraction.application.use_cases.extract_entities_from_document import (
    ExtractEntitiesFromDocumentUseCase,
)
from extraction.domain.entities import (
    DocumentInput,
    ExtractedEntity,
    ExtractedRelationship,
    ResolutionCandidate,
)
from shared_kernel.domain.value_objects import (
    SourceType,
    EntityId,
    Confidence,
    SourceProvenance,
    EntityKind,
)


def test_execute_orchestrates_extraction_and_resolution():
    mock_extractor = Mock()
    mock_resolver = Mock()

    doc = DocumentInput(
        document_id="doc-123",
        source_type=SourceType.COURT_JUDGMENT,
        raw_text="Ravi Kumar transferred funds.",
    )

    provenance = SourceProvenance(
        SourceType.COURT_JUDGMENT, "doc-123", datetime.utcnow()
    )

    entities = [
        ExtractedEntity(
            EntityId("e1"), EntityKind.PERSON, "Ravi Kumar", Confidence(0.9), provenance
        ),
    ]
    relationships = []

    mock_extractor.extract.return_value = (entities, relationships)

    candidates = [ResolutionCandidate(EntityId("e1"), EntityId("e2"), 0.95)]
    mock_resolver.find_candidates.return_value = candidates

    use_case = ExtractEntitiesFromDocumentUseCase(mock_extractor, mock_resolver)

    res_entities, res_rels, res_cands = use_case.execute(doc)

    assert res_entities == entities
    assert res_rels == relationships
    assert res_cands == candidates

    mock_extractor.extract.assert_called_once_with(doc)
    mock_resolver.find_candidates.assert_called_once_with(entities)

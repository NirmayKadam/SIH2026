"""
Extraction REST boundary. Mainly used internally by the worker, but exposed for
manual re-run/testing during the hackathon:

  POST /api/extraction/documents/{document_id}/extract   re-run extraction on a document
"""
from fastapi import APIRouter, Depends

from extraction.application.use_cases.extract_entities_from_document import (
    ExtractEntitiesFromDocumentUseCase,
)
from extraction.interface.rest.schemas import ExtractionResultResponseDTO
from ingestion.domain.entities import RawDocument

router = APIRouter(prefix="/api/extraction", tags=["extraction"])


def get_use_case() -> ExtractEntitiesFromDocumentUseCase:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_raw_document(document_id: str) -> RawDocument:
    # Real lookup against wherever ingested RawDocuments are held (Redis/DB) — implement
    # alongside the ingestion pipeline. NOT a placeholder return.
    raise NotImplementedError("Implement real RawDocument lookup by id")


@router.post("/documents/{document_id}/extract", response_model=ExtractionResultResponseDTO)
def extract_document(
    document_id: str,
    use_case: ExtractEntitiesFromDocumentUseCase = Depends(get_use_case),
) -> ExtractionResultResponseDTO:
    document = get_raw_document(document_id)
    entities, relationships, candidates = use_case.execute(document)
    return ExtractionResultResponseDTO(
        document_id=document_id,
        entities=[e.__dict__ for e in entities],
        relationships=[r.__dict__ for r in relationships],
        resolution_candidates=[c.__dict__ for c in candidates],
    )

"""
Ingestion REST boundary. Endpoints:

  POST /api/ingestion/documents        submit a real source path for async ingestion
  GET  /api/ingestion/documents/{id}    check job status

This router is the ONLY place ingestion exposes itself externally. Internally, other
contexts should not call these HTTP endpoints — they'd get access via the composition
root's wired-up ports instead (see api_gateway/di_container.py).
"""
from fastapi import APIRouter, Depends, HTTPException

from ingestion.application.use_cases.ingest_document import IngestDocumentUseCase
from ingestion.application.ports.job_queue_port import IngestionJobQueuePort
from ingestion.interface.rest.schemas import (
    IngestDocumentRequestDTO,
    IngestDocumentResponseDTO,
    IngestionJobStatusResponseDTO,
)
from shared_kernel.domain.errors import NotFoundError

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


def get_use_case() -> IngestDocumentUseCase:
    # Overridden by api_gateway/di_container.py at startup with the real wired adapter.
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


def get_job_queue() -> IngestionJobQueuePort:
    raise NotImplementedError("Dependency not wired — see api_gateway/di_container.py")


@router.post("/documents", response_model=IngestDocumentResponseDTO)
def submit_document(
    body: IngestDocumentRequestDTO,
    use_case: IngestDocumentUseCase = Depends(get_use_case),
) -> IngestDocumentResponseDTO:
    job_id = use_case.execute(source_type=body.source_type, source_path=body.source_path)
    return IngestDocumentResponseDTO(job_id=job_id)


@router.get("/documents/{job_id}", response_model=IngestionJobStatusResponseDTO)
def get_document_status(
    job_id: str,
    job_queue: IngestionJobQueuePort = Depends(get_job_queue),
) -> IngestionJobStatusResponseDTO:
    try:
        job = job_queue.get_status(job_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Ingestion job {job_id} not found")
    return IngestionJobStatusResponseDTO(
        job_id=job.job_id, status=job.status.value, error_message=job.error_message
    )

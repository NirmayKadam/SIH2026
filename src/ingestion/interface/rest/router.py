"""
Ingestion REST boundary. Endpoints:

  POST /api/ingestion/documents        submit a real source path for async ingestion
  GET  /api/ingestion/documents/{id}    check job status

This router is the ONLY place ingestion exposes itself externally. Internally, other
contexts should not call these HTTP endpoints — they'd get access via the composition
root's wired-up ports instead (see api_gateway/di_container.py).
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import shutil
import uuid
from pathlib import Path


from ingestion.application.use_cases.ingest_document import IngestDocumentUseCase
from ingestion.application.ports.job_queue_port import IngestionJobQueuePort
from ingestion.interface.rest.schemas import (
    IngestDocumentRequestDTO,
    IngestDocumentResponseDTO,
    IngestionJobStatusResponseDTO,
    UploadDocumentResponseDTO,
    UploadResult,
)
from shared_kernel.domain.errors import NotFoundError
from shared_kernel.domain.value_objects import SourceType

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


@router.post("/upload", response_model=UploadDocumentResponseDTO)
def upload_document(
    source_type: SourceType = Form(...),
    files: list[UploadFile] = File(...),
    use_case: IngestDocumentUseCase = Depends(get_use_case),
) -> UploadDocumentResponseDTO:
    results = []
    
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        if not file.filename:
            continue
            
        ext = Path(file.filename).suffix.lower()
        if ext not in {".csv", ".mbox", ".pdf", ".txt", ".eml"}:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        
        safe_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        job_id = use_case.execute(source_type=source_type, source_path=str(file_path))
        
        results.append(UploadResult(
            job_id=job_id,
            filename=file.filename,
            status="queued"
        ))
        
    return UploadDocumentResponseDTO(results=results)



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

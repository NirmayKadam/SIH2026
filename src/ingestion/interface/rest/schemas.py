from pydantic import BaseModel
from shared_kernel.domain.value_objects import SourceType


class IngestDocumentRequestDTO(BaseModel):
    source_type: SourceType
    source_path: str  # path under data/raw/, e.g. "icij_offshore_leaks/nodes-entities.csv"


class IngestDocumentResponseDTO(BaseModel):
    job_id: str


class IngestionJobStatusResponseDTO(BaseModel):
    job_id: str
    status: str
    error_message: str | None = None

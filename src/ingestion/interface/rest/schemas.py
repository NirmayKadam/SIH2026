from pydantic import BaseModel
from shared_kernel.domain.value_objects import SourceType


from shared_kernel.interface.validators import SanitizedString

class IngestDocumentRequestDTO(BaseModel):
    source_type: SourceType
    source_path: SanitizedString  # path under data/raw/, e.g. "icij_offshore_leaks/nodes-entities.csv"


class IngestDocumentResponseDTO(BaseModel):
    job_id: str


class UploadResult(BaseModel):
    job_id: str
    filename: str
    status: str


class UploadDocumentResponseDTO(BaseModel):
    results: list[UploadResult]



class IngestionJobStatusResponseDTO(BaseModel):
    job_id: str
    status: str
    error_message: str | None = None

from pydantic import BaseModel


class ExtractionResultResponseDTO(BaseModel):
    document_id: str
    entities: list[dict]
    relationships: list[dict]
    resolution_candidates: list[dict]

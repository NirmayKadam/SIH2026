from pydantic import BaseModel


class SourceProvenanceDTO(BaseModel):
    source_type: str
    source_document_id: str
    ingested_at: str


class GraphNodeResponseDTO(BaseModel):
    entity_id: str
    kind: str
    name: str
    confidence: float
    provenances: list[SourceProvenanceDTO]


class GraphEdgeResponseDTO(BaseModel):
    source_entity_id: str
    target_entity_id: str
    kind: str
    confidence: float
    provenances: list[SourceProvenanceDTO]


class NeighborhoodResponseDTO(BaseModel):
    center: GraphNodeResponseDTO
    nodes: list[GraphNodeResponseDTO]
    edges: list[GraphEdgeResponseDTO]


class EntityListResponseDTO(BaseModel):
    entities: list[GraphNodeResponseDTO]
    total: int


class GraphStatsResponseDTO(BaseModel):
    total_nodes: int
    total_edges: int

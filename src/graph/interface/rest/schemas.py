from pydantic import BaseModel


class GraphNodeResponseDTO(BaseModel):
    entity_id: str
    kind: str
    name: str
    confidence: float


class GraphEdgeResponseDTO(BaseModel):
    source_entity_id: str
    target_entity_id: str
    kind: str
    confidence: float


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

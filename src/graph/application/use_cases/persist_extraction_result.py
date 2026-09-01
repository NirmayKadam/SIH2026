from extraction.domain.entities import ExtractedEntity, ExtractedRelationship
from graph.application.ports.graph_repository_port import GraphRepositoryPort
from graph.domain.entities import GraphNode, GraphEdge


class PersistExtractionResultUseCase:
    """Writes Extraction context output into the graph. Called by the worker after
    ExtractEntitiesFromDocumentUseCase completes."""

    def __init__(self, repository: GraphRepositoryPort) -> None:
        self.repository = repository

    def execute(
        self, entities: list[ExtractedEntity], relationships: list[ExtractedRelationship]
    ) -> None:
        for e in entities:
            self.repository.upsert_node(
                GraphNode(
                    entity_id=e.entity_id, kind=e.kind, name=e.name,
                    confidence=e.confidence.score,
                    provenances=[e.provenance],
                    geo_point=e.geo_point,
                    properties=e.properties,
                )
            )
        for r in relationships:
            self.repository.upsert_edge(
                GraphEdge(
                    source_entity_id=r.source_entity_id,
                    target_entity_id=r.target_entity_id,
                    kind=r.kind,
                    confidence=r.confidence.score,
                    provenances=[r.provenance],
                    valid_from=r.valid_from,
                    valid_to=r.valid_to,
                    properties=r.properties,
                )
            )

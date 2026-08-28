from extraction.application.ports.extraction_port import EntityExtractionPort
from extraction.domain.entities import DocumentInput, ExtractedEntity, ExtractedRelationship
from shared_kernel.domain.value_objects import SourceType

class RoutingEntityExtractorAdapter(EntityExtractionPort):
    """
    Routes document extraction to the appropriate concrete extractor based on SourceType.
    Structured data (e.g. ICIJ CSVs) gets routed to a deterministic extractor to bypass the LLM,
    saving cost, latency, and strictly mapping known graph schema. Unstructured data goes to the LLM.
    """

    def __init__(
        self, 
        icij_extractor: EntityExtractionPort,
        gemini_extractor: EntityExtractionPort
    ) -> None:
        self._icij_extractor = icij_extractor
        self._gemini_extractor = gemini_extractor

    def extract(self, document: DocumentInput) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
        if document.source_type == SourceType.ICIJ_OFFSHORE_LEAKS:
            return self._icij_extractor.extract(document)
        else:
            return self._gemini_extractor.extract(document)

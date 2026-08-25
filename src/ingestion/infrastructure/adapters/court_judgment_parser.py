from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.errors import ExternalServiceError


class CourtJudgmentParserAdapter(DocumentParserPort):
    """Parses real, publicly published court judgment text/PDF files placed in
    data/raw/court_judgments/ (sourced manually — see docs/data-provenance.md for which
    specific judgments were selected and why). NOT YET IMPLEMENTED."""

    def parse(self, source_path: str) -> list[RawDocument]:
        raise NotImplementedError(
            "Implement real court judgment parsing (PDF/text extraction) here."
        )

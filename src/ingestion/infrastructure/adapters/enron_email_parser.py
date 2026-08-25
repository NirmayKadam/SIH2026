from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.errors import ExternalServiceError


class EnronEmailParserAdapter(DocumentParserPort):
    """Parses real Enron email corpus files (mbox or per-custodian folders) downloaded via
    scripts/load_enron_dataset.py. NOT YET IMPLEMENTED — see IcijCsvParserAdapter docstring
    for the same rule: real files only, raise on missing data, never fabricate."""

    def parse(self, source_path: str) -> list[RawDocument]:
        raise NotImplementedError(
            "Implement real Enron email parsing here. Confirm which custodians/date range "
            "are in scope in docs/data-provenance.md before building this."
        )

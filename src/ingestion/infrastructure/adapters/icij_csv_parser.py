from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError


class IcijCsvParserAdapter(DocumentParserPort):
    """Parses real ICIJ Offshore Leaks CSV exports (nodes-entities.csv, nodes-officers.csv,
    nodes-intermediaries.csv, relationships.csv) downloaded via scripts/load_icij_dataset.py.

    NOT YET IMPLEMENTED — build this against the actual downloaded CSVs. Do not stub this
    with fabricated rows; if the file isn't downloaded yet, this must raise, not fake data.
    """

    def parse(self, source_path: str) -> list[RawDocument]:
        raise NotImplementedError(
            "Implement real ICIJ CSV parsing here once data/raw/icij_offshore_leaks/ "
            "is populated by scripts/load_icij_dataset.py. See docs/data-provenance.md "
            "for the confirmed jurisdiction/firm subsample scope once decided."
        )

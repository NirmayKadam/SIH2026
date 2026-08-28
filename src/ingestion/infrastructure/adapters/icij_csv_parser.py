import csv
import json
import uuid
from pathlib import Path
from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError


ICIJ_CSV_FILES = [
    "nodes-entities.csv",
    "nodes-officers.csv",
    "nodes-intermediaries.csv",
    "nodes-addresses.csv",
    "nodes-others.csv",
    "relationships.csv",
]


class IcijCsvParserAdapter(DocumentParserPort):
    """Parses real ICIJ Offshore Leaks CSV exports. Accepts either:
    - A single CSV file path
    - A directory containing the standard ICIJ CSV files (nodes-entities.csv,
      nodes-officers.csv, relationships.csv, etc.)

    Each CSV row becomes one RawDocument with JSON-serialized row as raw_text.
    """

    def parse(self, source_path: str) -> list[RawDocument]:
        path = Path(source_path)

        if path.is_file():
            return self.parse_single_csv(path)

        if path.is_dir():
            return self.parse_directory(path)

        raise ExternalServiceError(
            f"ICIJ source path not found (expected file or directory): {source_path}"
        )

    def parse_directory(self, directory: Path) -> list[RawDocument]:
        """Parse all recognized ICIJ CSV files in a directory."""
        documents: list[RawDocument] = []
        csv_files = [directory / name for name in ICIJ_CSV_FILES if (directory / name).is_file()]

        if not csv_files:
            all_csvs = list(directory.glob("*.csv"))
            if not all_csvs:
                raise ExternalServiceError(
                    f"No CSV files found in ICIJ directory: {directory}"
                )
            csv_files = all_csvs

        for csv_path in csv_files:
            documents.extend(self.parse_single_csv(csv_path))

        return documents

    def parse_single_csv(self, csv_path: Path) -> list[RawDocument]:
        """Parse a single CSV file into RawDocument objects."""
        if not csv_path.is_file():
            raise ExternalServiceError(f"ICIJ CSV file not found: {csv_path}")

        documents: list[RawDocument] = []
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_text = json.dumps(row)
                    documents.append(
                        RawDocument(
                            document_id=str(uuid.uuid4()),
                            source_type=SourceType.ICIJ_OFFSHORE_LEAKS,
                            raw_text=raw_text,
                            source_path=str(csv_path),
                        )
                    )
        except Exception as exc:
            raise ExternalServiceError(
                f"Failed to parse ICIJ CSV {csv_path}: {exc}"
            ) from exc

        return documents

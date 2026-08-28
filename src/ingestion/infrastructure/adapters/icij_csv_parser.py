import csv
import json
import uuid
from pathlib import Path
from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError

class IcijCsvParserAdapter(DocumentParserPort):
    """Parses real ICIJ Offshore Leaks CSV exports (nodes-entities.csv, nodes-officers.csv,
    nodes-intermediaries.csv, relationships.csv) downloaded via scripts/load_icij_dataset.py.
    """

    def parse(self, source_path: str) -> list[RawDocument]:
        documents = []
        path = Path(source_path)
        
        if not path.is_file():
            raise ExternalServiceError(f"ICIJ CSV file not found: {source_path}")
            
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_text = json.dumps(row)
                    documents.append(
                        RawDocument(
                            document_id=str(uuid.uuid4()),
                            source_type=SourceType.ICIJ_OFFSHORE_LEAKS,
                            raw_text=raw_text,
                            source_path=str(path)
                        )
                    )
        except Exception as e:
            raise ExternalServiceError(f"Failed to parse ICIJ CSV {source_path}: {e}")
            
        return documents

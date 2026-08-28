import uuid
from pathlib import Path
from ingestion.application.ports.parser_port import DocumentParserPort
from ingestion.domain.entities import RawDocument
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError

try:
    import pymupdf4llm
except ImportError:
    pymupdf4llm = None

class CourtJudgmentParserAdapter(DocumentParserPort):
    """Parses real, publicly published court judgment text/PDF files placed in
    data/raw/court_judgments/ using pymupdf4llm for markdown extraction.
    """

    def parse(self, source_path: str) -> list[RawDocument]:
        if pymupdf4llm is None:
            raise ExternalServiceError("pymupdf4llm is not installed. Add it to dependencies.")
            
        path = Path(source_path)
        if not path.is_file():
            raise ExternalServiceError(f"Court judgment file not found: {source_path}")
            
        try:
            md_text = pymupdf4llm.to_markdown(str(path))
            return [
                RawDocument(
                    document_id=str(uuid.uuid4()),
                    source_type=SourceType.COURT_JUDGMENT,
                    raw_text=md_text,
                    source_path=str(path)
                )
            ]
        except Exception as e:
            raise ExternalServiceError(f"Failed to parse court judgment {source_path}: {e}")

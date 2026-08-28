import os
from pathlib import Path
from ingestion.infrastructure.adapters.court_judgment_parser import CourtJudgmentParserAdapter
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError
import pytest

def test_court_judgment_parser_success():
    parser = CourtJudgmentParserAdapter()
    sample_path = Path("data/samples/court_sample.pdf")
    
    if not sample_path.exists():
        pytest.skip(f"Sample data not found: {sample_path}")
        
    documents = parser.parse(str(sample_path))
    
    assert len(documents) == 1
    doc = documents[0]
    assert doc.source_type == SourceType.COURT_JUDGMENT
    assert doc.document_id is not None
    # PyMuPDF4LLM might output markdown, check for text inclusion
    assert "Supreme Court of India" in doc.raw_text
    assert "Judgment for Case XYZ vs ABC" in doc.raw_text

def test_court_judgment_parser_not_found():
    parser = CourtJudgmentParserAdapter()
    with pytest.raises(ExternalServiceError):
        parser.parse("data/samples/does_not_exist.pdf")

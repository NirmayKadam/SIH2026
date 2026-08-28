import os
from pathlib import Path
from ingestion.infrastructure.adapters.enron_email_parser import EnronEmailParserAdapter
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError
import pytest

def test_enron_email_parser_success():
    parser = EnronEmailParserAdapter()
    sample_path = Path("data/samples/enron_sample.mbox")
    
    if not sample_path.exists():
        pytest.skip(f"Sample data not found: {sample_path}")
        
    documents = parser.parse(str(sample_path))
    
    assert len(documents) == 1
    doc = documents[0]
    assert doc.source_type == SourceType.ENRON_EMAILS
    assert doc.document_id is not None
    assert "From: ceo@enron.com" in doc.raw_text
    assert "To: vp@enron.com" in doc.raw_text
    assert "Project Alpha Update" in doc.raw_text
    assert "test email body regarding Project Alpha." in doc.raw_text

def test_enron_email_parser_not_found():
    parser = EnronEmailParserAdapter()
    with pytest.raises(ExternalServiceError):
        parser.parse("data/samples/does_not_exist.mbox")

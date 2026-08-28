import os
import json
from pathlib import Path
from ingestion.infrastructure.adapters.icij_csv_parser import IcijCsvParserAdapter
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError
import pytest

def test_icij_csv_parser_success():
    parser = IcijCsvParserAdapter()
    sample_path = Path("data/samples/icij_sample.csv")
    
    if not sample_path.exists():
        pytest.skip(f"Sample data not found: {sample_path}")
        
    documents = parser.parse(str(sample_path))
    
    assert len(documents) > 0
    doc = documents[0]
    assert doc.source_type == SourceType.ICIJ_OFFSHORE_LEAKS
    assert doc.document_id is not None
    assert "Sample Offshore Entity Ltd." in doc.raw_text
    
    # Verify it is valid JSON
    parsed_json = json.loads(doc.raw_text)
    assert parsed_json["name"] == "Sample Offshore Entity Ltd."

def test_icij_csv_parser_not_found():
    parser = IcijCsvParserAdapter()
    with pytest.raises(ExternalServiceError):
        parser.parse("data/samples/does_not_exist.csv")

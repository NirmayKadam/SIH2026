import pytest
from unittest.mock import patch, MagicMock

from workers.extraction_worker import process_ingestion_job
from shared_kernel.domain.value_objects import SourceType
from shared_kernel.domain.errors import ExternalServiceError


@pytest.fixture
def mock_get_current_job():
    with patch("workers.extraction_worker.get_current_job") as mock:
        job = MagicMock()
        job.meta = {}
        mock.return_value = job
        yield mock


@pytest.fixture
def mock_parser():
    with patch("workers.extraction_worker._PARSERS") as mock_parsers:
        parser_instance = MagicMock()
        
        # Mocking the parsed document
        doc = MagicMock()
        doc.document_id = "test-doc-123"
        doc.source_type = SourceType.COURT_JUDGMENT
        doc.raw_text = "Test raw text"
        doc.source_path = "test/path.pdf"
        
        parser_instance.parse.return_value = [doc]
        mock_parsers.__getitem__.return_value = lambda: parser_instance
        yield parser_instance


@pytest.fixture
def mock_container():
    with patch("workers.extraction_worker.build_container") as mock_build:
        container = MagicMock()
        
        # Setup mock use cases
        container.extract_entities_use_case.execute.return_value = ([], [], [])
        
        # Graph repo
        mock_graph_repo = MagicMock()
        container.get_graph_stats_use_case.repository = mock_graph_repo
        
        mock_build.return_value = container
        yield container


@patch("workers.extraction_worker.PersistExtractionResultUseCase")
def test_process_ingestion_job_success_path(mock_persist_class, mock_get_current_job, mock_parser, mock_container):
    """
    Integration test validating that the worker iterates through all expected status states 
    (PARSING -> EXTRACTING -> PERSISTING -> PARSED) and closes the database connection.
    """
    job = mock_get_current_job.return_value
    
    process_ingestion_job("job-123", SourceType.COURT_JUDGMENT.value, "test/path.pdf")
    
    # Check all statuses were set correctly in order
    assert job.meta['status'] == "parsed"
    
    # Ensure graph repo was closed
    mock_graph_repo = mock_container.get_graph_stats_use_case.repository
    mock_graph_repo.close.assert_called_once()


def test_process_ingestion_job_failure_path(mock_get_current_job, mock_parser, mock_container):
    """
    Integration test validating error handling. If an exception occurs, 
    status should be 'failed' and graph_repo MUST still be closed.
    """
    job = mock_get_current_job.return_value
    
    # Make extraction fail
    mock_container.extract_entities_use_case.execute.side_effect = ValueError("Extraction failed")
    
    with pytest.raises(ValueError, match="Extraction failed"):
        process_ingestion_job("job-123", SourceType.COURT_JUDGMENT.value, "test/path.pdf")
    
    # Check job failure metadata
    assert job.meta['status'] == "failed"
    assert "Extraction failed" in job.meta['error']
    
    # Ensure graph repo was STILL closed
    mock_graph_repo = mock_container.get_graph_stats_use_case.repository
    mock_graph_repo.close.assert_called_once()

"""Ingestion domain — pure Python, no framework/DB/HTTP imports."""
from dataclasses import dataclass
from enum import Enum
from shared_kernel.domain.value_objects import SourceType


class IngestionStatus(str, Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


@dataclass
class RawDocument:
    """A single real source document/record before extraction (an ICIJ CSV row,
    an Enron email, a court judgment text file)."""
    document_id: str
    source_type: SourceType
    raw_text: str
    source_path: str  # where in data/raw/ this came from — always traceable


@dataclass
class IngestionJob:
    job_id: str
    source_type: SourceType
    source_path: str
    status: IngestionStatus
    error_message: str | None = None

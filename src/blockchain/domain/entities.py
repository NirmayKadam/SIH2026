from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class EvidenceRecord:
    """Represents a piece of evidence whose hash has been submitted to the blockchain ledger."""
    evidence_hash: str
    source_document_id: str
    transaction_id: str
    timestamp: datetime

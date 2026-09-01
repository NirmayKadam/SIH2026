import json
import os
import uuid
from datetime import datetime, timezone
from blockchain.application.ports.smart_contract_port import SmartContractPort
from shared_kernel.domain.value_objects import EvidenceHash
from shared_kernel.domain.errors import DuplicateEvidenceError, ExternalServiceError


class LocalFileLedgerAdapter(SmartContractPort):
    """
    Simulates a blockchain ledger using a local append-only JSONL file.
    Rejects ingestion if the hash already exists in the ledger.
    """

    def __init__(self, ledger_file_path: str = "data/ledger.jsonl") -> None:
        self._ledger_file_path = ledger_file_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(self._ledger_file_path), exist_ok=True)
        if not os.path.exists(self._ledger_file_path):
            with open(self._ledger_file_path, "w") as f:
                pass  # create empty file

    def store_hash(self, document_id: str, hash_val: EvidenceHash, metadata: dict) -> str:
        try:
            # Check for duplicates
            with open(self._ledger_file_path, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if record.get("evidence_hash") == hash_val.value:
                        raise DuplicateEvidenceError(f"Evidence hash {hash_val.value} already exists in the ledger.")
            
            # If no duplicate, append the new record
            tx_id = f"tx_{uuid.uuid4().hex}"
            record = {
                "transaction_id": tx_id,
                "document_id": document_id,
                "evidence_hash": hash_val.value,
                "metadata": metadata,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            with open(self._ledger_file_path, "a") as f:
                f.write(json.dumps(record) + "\n")
                
            return tx_id
            
        except DuplicateEvidenceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(f"Failed to interact with local ledger: {exc}")

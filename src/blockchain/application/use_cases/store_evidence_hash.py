from shared_kernel.domain.value_objects import EvidenceHash
from blockchain.application.ports.smart_contract_port import SmartContractPort
from blockchain.domain.entities import EvidenceRecord
from datetime import datetime, timezone

class StoreEvidenceHashUseCase:
    """
    Orchestrates the process of receiving an evidence hash and pushing it to the ledger.
    """

    def __init__(self, smart_contract_port: SmartContractPort) -> None:
        self._port = smart_contract_port

    def execute(self, document_id: str, hash_val_str: str, metadata: dict) -> EvidenceRecord:
        """
        Stores the hash and returns the EvidenceRecord.
        Raises DuplicateEvidenceError if the hash is already in the ledger.
        """
        hash_val = EvidenceHash(hash_val_str)
        tx_id = self._port.store_hash(document_id, hash_val, metadata)
        
        return EvidenceRecord(
            evidence_hash=hash_val.value,
            source_document_id=document_id,
            transaction_id=tx_id,
            timestamp=datetime.now(timezone.utc)
        )

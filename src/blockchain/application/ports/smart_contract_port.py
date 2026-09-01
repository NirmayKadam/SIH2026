from abc import ABC, abstractmethod
from shared_kernel.domain.value_objects import EvidenceHash


class SmartContractPort(ABC):
    """
    Port for interacting with a blockchain ledger to store immutable evidence hashes.
    """

    @abstractmethod
    def store_hash(self, document_id: str, hash_val: EvidenceHash, metadata: dict) -> str:
        """
        Stores the given evidence hash onto the ledger.

        Args:
            document_id: The ID of the document being hashed.
            hash_val: The cryptographic hash of the raw document.
            metadata: Additional metadata (e.g., source type, timestamp).

        Returns:
            The transaction ID (or equivalent) of the ledger record.

        Raises:
            DuplicateEvidenceError: If the hash is already present in the ledger.
            ExternalServiceError: If the ledger interaction fails.
        """
        pass

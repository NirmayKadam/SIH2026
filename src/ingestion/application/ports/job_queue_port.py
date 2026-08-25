from abc import ABC, abstractmethod
from ingestion.domain.entities import IngestionJob


class IngestionJobQueuePort(ABC):
    """Port for enqueueing async ingestion/extraction work (implemented by the RQ adapter)."""

    @abstractmethod
    def enqueue(self, job: IngestionJob) -> str:
        """Returns the queue job id."""
        ...

    @abstractmethod
    def get_status(self, job_id: str) -> IngestionJob:
        ...

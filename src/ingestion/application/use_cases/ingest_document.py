import uuid
from shared_kernel.domain.value_objects import SourceType
from ingestion.domain.entities import IngestionJob, IngestionStatus
from ingestion.application.ports.job_queue_port import IngestionJobQueuePort


class IngestDocumentUseCase:
    """Orchestrates: accept a real source path -> enqueue async parsing+extraction job.
    Does NOT parse synchronously — parsing/extraction happens in the worker (see
    src/workers/extraction_worker.py) so the API responds immediately."""

    def __init__(self, job_queue: IngestionJobQueuePort) -> None:
        self._job_queue = job_queue

    def execute(self, source_type: SourceType, source_path: str) -> str:
        job = IngestionJob(
            job_id=str(uuid.uuid4()),
            source_type=source_type,
            source_path=source_path,
            status=IngestionStatus.QUEUED,
        )
        return self._job_queue.enqueue(job)

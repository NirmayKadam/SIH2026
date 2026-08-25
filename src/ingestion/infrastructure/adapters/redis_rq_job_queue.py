"""
Real Redis + RQ (Redis Queue) adapter — this is the async boundary that keeps the API
responsive while slow LLM-calling extraction work happens in the background worker
(see src/workers/extraction_worker.py). Requires REDIS_URL (see .env.example).
"""
import os
import json

import redis
from rq import Queue
from rq.job import Job

from ingestion.application.ports.job_queue_port import IngestionJobQueuePort
from ingestion.domain.entities import IngestionJob, IngestionStatus
from shared_kernel.domain.errors import ExternalServiceError, NotFoundError

QUEUE_NAME = "extraction_jobs"


class RedisRqJobQueueAdapter(IngestionJobQueuePort):
    def __init__(self) -> None:
        redis_url = os.environ.get("REDIS_URL")
        if not redis_url:
            raise ExternalServiceError("REDIS_URL is not set — see .env.example")
        try:
            self._redis = redis.from_url(redis_url)
            self._redis.ping()
        except Exception as exc:
            raise ExternalServiceError(f"Could not connect to Redis at {redis_url}: {exc}") from exc
        self._queue = Queue(QUEUE_NAME, connection=self._redis)

    def enqueue(self, job: IngestionJob) -> str:
        # Enqueues the worker function by import path — see workers/extraction_worker.py
        rq_job = self._queue.enqueue(
            "workers.extraction_worker.process_ingestion_job",
            job.job_id, job.source_type.value, job.source_path,
            job_id=job.job_id,
        )
        return rq_job.id

    def get_status(self, job_id: str) -> IngestionJob:
        try:
            rq_job = Job.fetch(job_id, connection=self._redis)
        except Exception as exc:
            raise NotFoundError(f"Ingestion job {job_id} not found") from exc

        status_map = {
            "queued": IngestionStatus.QUEUED,
            "started": IngestionStatus.PARSING,
            "finished": IngestionStatus.PARSED,
            "failed": IngestionStatus.FAILED,
        }
        return IngestionJob(
            job_id=job_id,
            source_type=rq_job.args[1],
            source_path=rq_job.args[2],
            status=status_map.get(rq_job.get_status(), IngestionStatus.QUEUED),
            error_message=str(rq_job.exc_info) if rq_job.is_failed else None,
        )

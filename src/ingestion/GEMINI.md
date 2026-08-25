# Ingestion Context — GEMINI.md

## Responsibility

Parse raw source files (ICIJ CSV, Enron mbox/CSV, court judgment PDF/text) into
`RawDocument` objects and enqueue them for async extraction via Redis/RQ.

## Domain Types (`domain/entities.py`)

### `RawDocument`
```python
@dataclass
class RawDocument:
    document_id: str       # UUID assigned at parse time
    source_type: SourceType  # from shared_kernel
    raw_text: str          # full text content of the source
    source_path: str       # relative path under data/raw/ — always traceable
```

### `IngestionJob`
```python
@dataclass
class IngestionJob:
    job_id: str
    source_type: SourceType
    source_path: str
    status: IngestionStatus  # QUEUED | PARSING | PARSED | FAILED
    error_message: str | None
```

## Ports

### `DocumentParserPort` (`application/ports/parser_port.py`)
```python
class DocumentParserPort(ABC):
    @abstractmethod
    def parse(self, source_path: str) -> list[RawDocument]: ...
```
One adapter per data source. Must parse real files only — raise `ExternalServiceError` on failure.

### `IngestionJobQueuePort` (`application/ports/job_queue_port.py`)
```python
class IngestionJobQueuePort(ABC):
    @abstractmethod
    def enqueue(self, job: IngestionJob) -> str: ...  # returns queue job ID

    @abstractmethod
    def get_status(self, job_id: str) -> IngestionJob: ...
```

## Use Cases

### `IngestDocumentUseCase`
- Input: `source_type: SourceType`, `source_path: str`
- Action: Creates `IngestionJob`, enqueues it via `IngestionJobQueuePort`
- Output: `job_id: str`
- Async: actual parsing happens in the worker (`src/workers/extraction_worker.py`)

## REST Endpoints

| Method | Route | Request | Response |
|---|---|---|---|
| POST | `/api/ingestion/documents` | `{source_type, source_path}` | `{job_id}` |
| GET | `/api/ingestion/documents/{job_id}` | — | `{job_id, status, error_message}` |

## Adapters to Implement

| Adapter | File | Status |
|---|---|---|
| `IcijCsvParserAdapter` | `infrastructure/adapters/icij_csv_parser.py` | Stub (`NotImplementedError`) |
| `EnronEmailParserAdapter` | `infrastructure/adapters/enron_email_parser.py` | Stub (`NotImplementedError`) |
| `CourtJudgmentParserAdapter` | `infrastructure/adapters/court_judgment_parser.py` | Stub (`NotImplementedError`) |
| `RedisRqJobQueueAdapter` | `infrastructure/adapters/redis_rq_job_queue.py` | Working skeleton |

## Allowed Imports

- `shared_kernel.domain.value_objects` (SourceType)
- `shared_kernel.domain.errors` (ExternalServiceError, NotFoundError)
- **Nothing else from other contexts**

## Data Sources

| Source | Parser | Input Path |
|---|---|---|
| ICIJ Offshore Leaks | `IcijCsvParserAdapter` | `data/raw/icij_offshore_leaks/` |
| Enron Emails | `EnronEmailParserAdapter` | `data/raw/enron_emails/` |
| Court Judgments | `CourtJudgmentParserAdapter` | `data/raw/court_judgments/` |

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
| `IcijCsvParserAdapter` | `infrastructure/adapters/icij_csv_parser.py` | Implemented |
| `EnronEmailParserAdapter` | `infrastructure/adapters/enron_email_parser.py` | Implemented |
| `CourtJudgmentParserAdapter` | `infrastructure/adapters/court_judgment_parser.py` | Implemented |
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

## Roadmap — Ingestion Tasks (Scoped to This Domain)

### File Upload Endpoint (HIGH PRIORITY — Owner: Nirmay)

Currently ingestion only accepts server-side path. Need actual file upload for demo.

- [ ] New endpoint: `POST /api/ingestion/upload` — accepts `multipart/form-data`
- [ ] Validate file type (`.csv`, `.mbox`, `.pdf`)
- [ ] Save uploaded file to `data/uploads/<uuid>_<filename>`
- [ ] Trigger same `IngestDocumentUseCase` pipeline as path-based endpoint
- [ ] Return `{ job_id, filename, status: "queued" }`
- [ ] Add `data/uploads/` to `.gitignore`

### Battle-Test Unstructured Extraction (Owner: Teammate B)

- [ ] Run `load_enron_dataset.py` inside Docker. Verify `EnronEmailParserAdapter` → `GeminiEntityExtractionAdapter` → Neo4j pipeline end-to-end
- [ ] Run `load_court_judgments.py`. Verify `CourtJudgmentParserAdapter` → LLM extraction produces real entities
- [ ] Tune Gemini extraction prompts for legal language and email threading
- [ ] Test with at least 5 real documents from each source

**Definition of Done:** Search for a person's name in UI and see connections from **multiple sources** (ICIJ + Enron or ICIJ + Court Judgment) in graph.

### New Data Modalities (Owner: Teammate E — Stretch)

- [ ] CDR parser: Find real anonymized CDR dataset. Build `CdrParserAdapter`
- [ ] Financial transaction parser: public financial dataset
- [ ] Add `SourceType.CDR` and `SourceType.FINANCIAL_TRANSACTION` to `shared_kernel`


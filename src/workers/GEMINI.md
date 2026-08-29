# Workers Context — GEMINI.md

## Responsibility

RQ background workers that execute the async pipeline:
`parse (Ingestion) → extract (Extraction) → persist (Graph)`

This runs outside the request/response cycle so the API can respond immediately
after enqueueing a job.

## Pipeline Flow

```
POST /api/ingestion/documents
  → IngestDocumentUseCase.enqueue()
    → Redis RQ queue "extraction_jobs"
      → extraction_worker.process_ingestion_job()
          1. Select parser by SourceType
          2. parser.parse(source_path) → list[RawDocument]
          3. Map RawDocument → DocumentInput (boundary mapping)
          4. extract_use_case.execute(document_input) → entities, relationships, candidates
          5. persist_use_case.execute(entities, relationships) → writes to Neo4j
```

## Boundary Mapping

Worker is the ONLY place that maps between Ingestion and Extraction types:

```python
from ingestion.domain.entities import RawDocument
from extraction.domain.entities import DocumentInput

# At the boundary:
document_input = DocumentInput(
    document_id=raw_document.document_id,
    source_type=raw_document.source_type,
    raw_text=raw_document.raw_text,
)
```

## Entry Point

```bash
rq worker extraction_jobs --url $REDIS_URL
```

File: `extraction_worker.py` → function: `process_ingestion_job(job_id, source_type_value, source_path)`

## Known Issues (To Fix)

1. **Worker creates its own adapters** instead of using DI from `di_container.py`.
   Duplicates wiring logic. Should be refactored to use a shared container builder.

2. **No job status updates.** Worker doesn't update `IngestionJob.status` back to
   Redis — `get_status()` won't reflect parsing/extraction progress.

3. **No error handling.** If `parser.parse()` or `extract_use_case.execute()` throws,
   job silently fails. Should catch, update job status to `FAILED`, and store error message.

4. **`graph_repo.close()` not in `finally` block.** Connection leak on error.

5. **Resolution candidates ignored.** Worker receives `_candidates` but drops them.
   Needs a real merge decision path — don't auto-merge blindly.

## Imports (Cross-Context — Expected)

Worker is an orchestration layer, so it legitimately imports from multiple contexts:
- `ingestion.infrastructure.adapters.*` — parsers
- `ingestion.domain.entities.RawDocument` — input type
- `extraction.application.use_cases.*` — extraction pipeline
- `extraction.domain.entities.DocumentInput` — mapped input type
- `extraction.infrastructure.adapters.*` — Gemini + rapidfuzz
- `graph.application.use_cases.*` — persistence
- `graph.infrastructure.adapters.*` — Neo4j
- `shared_kernel.domain.value_objects.SourceType`

## Running Locally

```bash
# via Docker Compose (recommended)
docker compose up worker

# or standalone
rq worker extraction_jobs --url redis://localhost:6379/0
```

## Roadmap — Workers Tasks (Scoped to This Domain)

### Fix Known Issues (Owner: Teammate F)

- [x] **DI duplication:** Worker creates its own adapters. Refactor to use shared container builder from `di_container.py`
- [x] **Job status updates:** Worker doesn't update `IngestionJob.status` back to Redis — `get_status()` won't reflect progress. Add status transitions: `PARSING → EXTRACTING → PERSISTING → DONE / FAILED`
- [x] **Error handling:** Catch errors from `parser.parse()` and `extract_use_case.execute()`, update job status to `FAILED`, store error message
- [x] **Connection leak:** `graph_repo.close()` not in `finally` block. Fix.
- [x] **Resolution candidates dropped:** Worker receives `_candidates` but ignores them. Implement real merge decision path


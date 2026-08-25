# Extraction Context — GEMINI.md

## Responsibility

Accept parsed document text (as `DocumentInput`), extract entities and
relationships via the Gemini LLM, and identify likely alias/duplicate entities
using string similarity (rapidfuzz).

## Domain Types (`domain/entities.py`)

### `DocumentInput` — Extraction's own input type
```python
@dataclass
class DocumentInput:
    document_id: str      # matches the ingestion RawDocument.document_id
    source_type: SourceType
    raw_text: str
```
**Important:** Extraction does NOT import `RawDocument` from Ingestion. The worker
maps `RawDocument → DocumentInput` at the pipeline boundary.

### `ExtractedEntity`
```python
@dataclass
class ExtractedEntity:
    entity_id: EntityId
    kind: EntityKind          # from shared_kernel
    name: str
    confidence: Confidence    # from shared_kernel — must be real model output
    provenance: SourceProvenance
```

### `ExtractedRelationship`
```python
@dataclass
class ExtractedRelationship:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind    # from shared_kernel
    confidence: Confidence
    provenance: SourceProvenance
```

### `ResolutionCandidate`
```python
@dataclass
class ResolutionCandidate:
    entity_a: EntityId
    entity_b: EntityId
    similarity_score: float   # genuinely computed (rapidfuzz ratio), never hardcoded
```

## Ports

### `EntityExtractionPort` (`application/ports/extraction_port.py`)
```python
class EntityExtractionPort(ABC):
    @abstractmethod
    def extract(self, document: DocumentInput) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]: ...
```
Must raise `ExternalServiceError` or `RateLimitExceededError` on failure — never
return empty list to mask a failed call.

### `IdentityResolutionPort` (`application/ports/identity_resolution_port.py`)
```python
class IdentityResolutionPort(ABC):
    @abstractmethod
    def find_candidates(self, entities: list[ExtractedEntity]) -> list[ResolutionCandidate]: ...
```

## Use Cases

### `ExtractEntitiesFromDocumentUseCase`
- Input: `DocumentInput`
- Action: calls `EntityExtractionPort.extract()` → `IdentityResolutionPort.find_candidates()`
- Output: `(entities, relationships, resolution_candidates)`

## REST Endpoints

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/extraction/documents/{document_id}/extract` | Re-run extraction (manual/testing) |

## Adapters

| Adapter | File | Notes |
|---|---|---|
| `GeminiEntityExtractionAdapter` | `infrastructure/adapters/gemini_entity_extractor.py` | Working — uses `gemini-2.5-flash-lite`, exponential backoff on 429 |
| `RapidFuzzIdentityResolutionAdapter` | `infrastructure/adapters/rapidfuzz_identity_resolver.py` | Working — pairwise name similarity |

## Gemini API Patterns

- Model: `gemini-2.5-flash-lite` (best free RPM/RPD)
- Prompt: structured JSON output schema (entities + relationships)
- Retry: exponential backoff (2s, 4s, 8s) on 429
- Confidence: comes from model's own output — never fabricated
- Env var: `GEMINI_API_KEY` (required, fail-fast)

## Allowed Imports

- `shared_kernel.domain.value_objects` (EntityId, Confidence, SourceProvenance, SourceType, EntityKind, RelationshipKind)
- `shared_kernel.domain.errors` (ExternalServiceError, RateLimitExceededError)
- **Nothing from ingestion, graph, analytics, or query**

## Downstream Consumer

The worker (`src/workers/extraction_worker.py`) calls this use case's `execute()`
and passes the results to `graph/application/use_cases/persist_extraction_result.py`.
Extraction does NOT write to the graph — that's Graph context's responsibility.

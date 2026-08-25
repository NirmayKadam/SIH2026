# Shared Kernel — GEMINI.md

## Purpose

Shared vocabulary types and error hierarchy used by ALL bounded contexts.
This is NOT a business domain — it's the minimal set of types that must be
consistent across contexts to avoid duplication and ensure type safety.

## What Belongs Here

Only types that 2+ contexts genuinely share. If only one context uses it, it
belongs in that context's domain — not here.

### Value Objects (`domain/value_objects.py`)

| Type | Purpose | Used By |
|---|---|---|
| `EntityKind` | Enum: `person`, `organization`, `account`, `location`, `event` | Extraction, Graph |
| `RelationshipKind` | Enum: `communicated_with`, `transacted_with`, `officer_of`, `intermediary_of`, `present_at`, `mentioned_with` | Extraction, Graph |
| `EntityId` | Wraps a `str` ID; validated non-empty | All contexts |
| `SourceType` | Enum: `icij_offshore_leaks`, `enron_emails`, `court_judgment` | Ingestion, Extraction |
| `SourceProvenance` | Tracks `source_type` + `source_document_id` + `ingested_at` | Extraction |
| `Confidence` | Float 0.0–1.0; must come from real computation (ARCHITECTURE.md rule 4) | Extraction |

### Error Hierarchy (`domain/errors.py`)

```
DomainError
├── NotFoundError          — entity/resource does not exist
├── ValidationError        — input violates a domain invariant
├── ExternalServiceError   — adapter failure (LLM, Neo4j, Redis, parser)
│   └── RateLimitExceededError — free-tier API rate limit
```

**Rule:** Adapters MUST raise `ExternalServiceError` (or subclass) on failure.
Never return an empty/default value that masks the failure.

### Events (`events/event_bus.py`)

Optional pub/sub event system. Currently scaffolded but not required for MVP.
If event bus costs more than ~2 hours, use direct port calls instead (see
ARCHITECTURE.md critic note #5).

## What Does NOT Belong Here

- Business logic (put in the owning context's `domain/`)
- Framework imports (FastAPI, Pydantic, Neo4j, etc.)
- Adapter code (infrastructure layer concern)
- DTOs (REST interface layer concern)

## Adding a New Shared Type

1. Verify 2+ contexts actually need it
2. Add to `domain/value_objects.py`
3. Update this GEMINI.md
4. Update the project root GEMINI.md

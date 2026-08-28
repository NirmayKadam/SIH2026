# GEMINI.md — AI-Powered Criminal Network Analysis System

## Project Overview

SIH 2026 — PS 26189, Ministry of Home Affairs / NCRB.

A Python (FastAPI) + Neo4j + React/vis-network system that ingests real-world
criminal/financial datasets (ICIJ Offshore Leaks, Enron emails, Indian court
judgments), extracts entities/relationships via Gemini LLM, builds a Neo4j
knowledge graph, runs graph analytics, and exposes a natural-language query
interface. Full architecture is in `ARCHITECTURE.md`.

## Tech Stack

### Backend (Python 3.11+, runs in Docker)
- **FastAPI 0.115** — REST API framework
- **Pydantic 2.9** — request/response DTOs (never raw domain entities)
- **Neo4j 5.24** — graph database (Community Edition, Bolt protocol)
- **Redis 5 + RQ 1.16** — async job queue for extraction pipeline
- **NetworkX 3.3** — graph analytics (centrality, community detection, shortest path)
- **google-generativeai 0.8** — Gemini API for entity extraction + NL intent classification
- **rapidfuzz 3.9** — string similarity for identity resolution / alias merging
- **python-dotenv** — `.env` loading
- **pytest 8.3** — testing

### Frontend (separate runtime)
- **React 18** + **Vite 5** — SPA
- **vis-network 9** — graph visualization

### Infrastructure
- **Docker Compose** — orchestrates `neo4j`, `redis`, `api`, `worker` services
- **Makefile** — `make up`, `make test`, `make load-icij`, etc.

## Architecture — Hexagonal / Ports & Adapters

Every bounded context under `src/` follows the same 4-layer structure:

```
<context>/
├── domain/            # Pure Python. Entities, value objects, domain services.
│                       #   NO framework imports, NO database code, NO HTTP.
├── application/
│   ├── ports/          # Abstract interfaces (e.g., GraphRepositoryPort)
│   └── use_cases/      # Orchestrate domain logic for one business action
├── infrastructure/
│   └── adapters/       # Concrete port implementations (Neo4j, Gemini, Redis…)
└── interface/
    └── rest/           # FastAPI router + Pydantic DTOs
```

**Dependency rule:** `interface → application → domain`. Infrastructure implements
`application/ports/` but domain/application never import infrastructure directly.

### Bounded Contexts

| Context | Folder | Responsibility |
|---|---|---|
| Ingestion | `src/ingestion/` | Parse raw sources (ICIJ CSV, Enron mbox, court PDFs) into common schema |
| Extraction | `src/extraction/` | LLM entity/relationship extraction, identity resolution (rapidfuzz) |
| Graph | `src/graph/` | Neo4j knowledge graph persistence, schema, triplet read/write |
| Analytics | `src/analytics/` | Centrality, community detection (Louvain), shortest path |
| Query | `src/query/` | NL intent classification → parameterized Cypher templates |
| API Gateway | `src/api_gateway/` | Composition root (NOT a business domain). Mounts routers, wires DI |
| Workers | `src/workers/` | RQ workers consuming async extraction jobs |
| Shared Kernel | `src/shared_kernel/` | `EntityId`, `Confidence`, `SourceProvenance`, `EntityKind`, `RelationshipKind`, base error types |
| Frontend | `frontend/` | React SPA with vis-network graph visualization |

### Shared Types (in `shared_kernel/domain/value_objects.py`)

These types are the shared vocabulary — every context imports them from here,
never defines its own copy:

- `EntityKind` — `person`, `organization`, `account`, `location`, `event`
- `RelationshipKind` — `communicated_with`, `transacted_with`, `officer_of`, `intermediary_of`, `present_at`, `mentioned_with`
- `EntityId` — wraps a string ID, validated non-empty
- `Confidence` — float 0.0–1.0, must come from real computation
- `SourceType` — `icij_offshore_leaks`, `enron_emails`, `court_judgment`
- `SourceProvenance` — tracks source type + document ID + timestamp

### Cross-Domain Import Rules

Each domain imports ONLY from `shared_kernel` and its own domain. One documented
exception: `graph/application/use_cases/persist_extraction_result.py` imports
Extraction domain types (`ExtractedEntity`, `ExtractedRelationship`) for the
pipeline handoff. No other cross-domain domain imports are allowed.

### Composition Root

`api_gateway/di_container.py` is the ONLY file that imports concrete adapter
classes. It wires infrastructure into ports and exposes use cases. No other module
should import a concrete adapter directly.

`api_gateway/main.py` mounts each context's router and uses
`app.dependency_overrides` to inject container-built use cases into FastAPI's
`Depends(...)`.

## REST API Surface

| Context | Method | Route | Purpose |
|---|---|---|---|
| Ingestion | POST | `/api/ingestion/documents` | Submit source for async ingestion |
| Ingestion | GET | `/api/ingestion/documents/{job_id}` | Check job status |
| Extraction | POST | `/api/extraction/documents/{document_id}/extract` | Re-run extraction |
| Graph | GET | `/api/graph/entities` | List/search entities (`?q=name&limit=20`) |
| Graph | GET | `/api/graph/entities/{entity_id}` | Single entity detail |
| Graph | GET | `/api/graph/entities/{entity_id}/neighbors` | N-hop neighborhood (`?depth=2`) |
| Graph | GET | `/api/graph/stats` | Node/edge counts |
| Analytics | GET | `/api/analytics/centrality` | Centrality scores (`?type=degree\|betweenness\|pagerank`) |
| Analytics | GET | `/api/analytics/communities` | Community detection |
| Analytics | GET | `/api/analytics/shortest-path` | Shortest path (`?source=X&target=Y`) |
| Query | POST | `/api/query/ask` | Natural language query |
| — | GET | `/health` | Health check |

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Files, folders, functions, vars | `snake_case` | `neo4j_graph_repository.py` |
| Classes | `PascalCase` | `ExtractedEntity` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_CONFIDENCE_THRESHOLD` |
| Ports | `<Noun>Port` in `application/ports/` | `GraphRepositoryPort` |
| Adapters | `<Tech><PortName>Adapter` | `Neo4jGraphRepositoryAdapter` |
| Use cases | verb-phrase file + `<VerbPhrase>UseCase` class | `extract_entities_from_document.py` → `ExtractEntitiesFromDocumentUseCase` |
| REST DTOs | `<Thing>RequestDTO` / `<Thing>ResponseDTO` | `ExtractEntitiesRequestDTO` |
| Domain events | past-tense verb | `EntityExtracted` |
| Tests | `test_` prefix, mirror source path | `tests/test_neo4j_graph_repository.py` |
| API routes | `/api/<context>/<resource>` | `/api/graph/entities/{id}` |

> **No leading underscores.** Never prefix any name (function, method, variable,
> class, module) with `_` or `__`. Use descriptive public names instead. Example:
> `record_to_node`, not `_record_to_node`. This applies to all code in the project.

## Hard Rules — NEVER Violate These

These are codified in `ARCHITECTURE.md` §5. All code changes must comply:

1. **No synthetic/mock data in application or infrastructure code.** Only real
   datasets (ICIJ, Enron, court judgments) flow through the running system. Test
   fixtures use real-but-subsampled data in `tests/fixtures/` or `data/samples/`.
2. **No silent fallbacks on failure.** If something fails, raise a typed domain
   exception from `shared_kernel/domain/errors.py` and propagate it. Never
   catch-and-return a fake success.
3. **No placeholder functions disguised as real.** A stub either raises
   `NotImplementedError` or doesn't exist — never `return {"status": "ok"}`
   without doing the work.
4. **No fabricated confidence scores.** Confidence values must come from real
   computation (model output, similarity metric) — never hardcoded.
5. **No hardcoded demo answers.** If the pipeline can't answer a query, the UI
   must show that honestly (`"no path found"` / `"extraction incomplete"`).
6. **Config fails fast.** Missing env vars cause startup failure — no silent
   fallback to fake/no-op clients. See `api_gateway/settings.py`.
7. **Every adapter commit must be tested against real data** — even a tiny slice.

## Error Handling

All domain exceptions inherit from `shared_kernel.domain.errors.DomainError`:

- `NotFoundError` — entity/resource does not exist
- `ValidationError` — input violates a domain invariant
- `ExternalServiceError` — adapter failure (LLM, Neo4j, Redis, file parser)
- `RateLimitExceededError` — free-tier API rate limit; callers must retry with backoff

Adapters MUST raise `ExternalServiceError` (or subclass) on failure. Never return
an empty/default value that masks the failure.

## API Security

To prevent API abuse and Cross-Site Scripting (XSS), the following measures are enforced:

1. **Global Rate Limiting**: A `slowapi` limiter is attached to the FastAPI app (`api_gateway/main.py`) which enforces a strict `"60/minute"` request limit per client IP across all API endpoints. Exceeding this triggers a `429 Too Many Requests` error.
2. **XSS Sanitization**: Pydantic schemas processing untrusted text input (e.g., `IngestDocumentRequestDTO.source_path`, `AskQuestionRequestDTO.question`) use `SanitizedString` from `shared_kernel.interface.validators`. This automatically strips all HTML tags using the `nh3` (ammonia) library before the request ever hits a use case.

## Environment Variables

All required; app refuses to start if any are missing (see `.env.example`):

| Variable | Purpose |
|---|---|
| `NEO4J_URI` | Bolt URI (e.g., `bolt://neo4j:7687`) |
| `NEO4J_USER` | Neo4j username |
| `NEO4J_PASSWORD` | Real password — no defaults |
| `REDIS_URL` | Redis connection string |
| `GEMINI_API_KEY` | Google Gemini API key (free tier OK) |

## Common Commands

```bash
cp .env.example .env           # fill in real values first
make up                        # docker compose up --build
make test                      # pytest inside the api container
make load-icij                 # load ICIJ Offshore Leaks subsample
make load-enron                # load Enron email subsample
make load-judgments            # load court judgment subsample
make down                      # tear down containers
```

- **API docs (Swagger):** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474
- **Frontend dev server:** `cd frontend && npm run dev`

## Development Workflow

1. **Define the Port** in `application/ports/` as an abstract interface.
2. **Implement the Use Case** in `application/use_cases/`, depending only on ports
   and domain objects.
3. **Build the Adapter** in `infrastructure/adapters/`, implementing the port.
4. **Wire it** in `api_gateway/di_container.py`.
5. **Expose it** via a FastAPI router in `interface/rest/router.py` with Pydantic
   DTOs. Add a placeholder `Depends(get_use_case)` function that the composition
   root will override.
6. **Test against real data** — adapters must be run against at least a subsampled
   real dataset before merging.

## Key Files

| File | Purpose |
|---|---|
| `ARCHITECTURE.md` | Full architecture plan, hard rules, 3-day sequencing |
| `src/api_gateway/main.py` | FastAPI entrypoint, router mounting |
| `src/api_gateway/di_container.py` | Composition root, all adapter wiring |
| `src/api_gateway/settings.py` | Fail-fast env config |
| `src/shared_kernel/domain/errors.py` | Base exception hierarchy |
| `src/shared_kernel/domain/value_objects.py` | `EntityId`, `Confidence`, `SourceProvenance`, `EntityKind`, `RelationshipKind` |
| `docker-compose.yml` | Service orchestration |
| `docs/data-provenance.md` | Dataset sources, licensing, subsample scope |
| `docs/domain-model.md` | Entity/relationship type glossary |

## Per-Domain GEMINI.md Files

Each bounded context has its own `GEMINI.md` scoped to that developer's needs:
- `src/shared_kernel/GEMINI.md`
- `src/ingestion/GEMINI.md`
- `src/extraction/GEMINI.md`
- `src/graph/GEMINI.md`
- `src/analytics/GEMINI.md`
- `src/query/GEMINI.md`
- `src/workers/GEMINI.md`
- `frontend/GEMINI.md`

## Testing

- **Unit tests** live inside each context's `tests/` folder.
- **Integration tests** live in `tests/integration/`.
- Test fixtures use real-but-subsampled data only.
- Run via `make test` (executes `pytest` inside the Docker container).
- `pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["src", "tests"]`.

## Datasets (Real Data Only)

| Dataset | Source | Data Dir |
|---|---|---|
| ICIJ Offshore Leaks | `icij.org/investigations/offshore-leaks` | `data/raw/icij_offshore_leaks/` |
| Enron Emails | Public Enron corpus | `data/raw/enron_emails/` |
| Indian Court Judgments | Real court judgment PDFs | `data/raw/court_judgments/` |

`data/raw/` is gitignored (large files). `data/samples/` contains small,
checked-in, real (not synthetic) slices for CI and demos.

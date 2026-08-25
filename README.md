# AI-Powered Criminal Network Analysis System

SIH 2026 — PS 26189 | Ministry of Home Affairs / NCRB

See **ARCHITECTURE.md** for the full plan, bounded contexts, naming conventions,
and hard rules (no mocks / no synthetic data / no silent fallbacks).

## Quickstart

```bash
cp .env.example .env
# fill in NEO4J_PASSWORD and GEMINI_API_KEY (free tier: https://aistudio.google.com/app/apikey)

make up          # starts neo4j, redis, api, worker
```

API docs (Swagger): http://localhost:8000/docs
Neo4j Browser: http://localhost:7474

## Load real data (once subsample scope is decided — see docs/data-provenance.md)

```bash
make load-icij
make load-enron
make load-judgments
```

## Run tests

```bash
make test
```

## Team ownership

| Context | Folder | Owner |
|---|---|---|
| Ingestion | `src/ingestion/` | Person A |
| Extraction | `src/extraction/` | Person B |
| Graph | `src/graph/` | Person C |
| Analytics | `src/analytics/` | Person D |
| Query + API Gateway | `src/query/`, `src/api_gateway/` | Person E |
| Frontend | `frontend/` | Person F (+G) |

Work inward: each owner builds their `infrastructure/adapters/` implementations
against their context's `application/ports/` interfaces. The REST contracts in
`interface/rest/router.py` are already defined — build against them.

# Graph Context — GEMINI.md

## Responsibility

Owns the Neo4j knowledge graph. Provides persistence (write entities/edges),
querying (neighborhood, search, detail, stats), and the pipeline handoff from
Extraction output → graph nodes/edges.

## Domain Types (`domain/entities.py`)

### `GraphNode`
```python
@dataclass
class GraphNode:
    entity_id: EntityId         # from shared_kernel
    kind: EntityKind            # from shared_kernel
    name: str
    confidence: float           # denormalized from Confidence.score at write time
    provenances: list[SourceProvenance] = field(default_factory=list)  # append-only, tracks all sources
```

### `GraphEdge`
```python
@dataclass
class GraphEdge:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind      # from shared_kernel
    confidence: float
    provenances: list[SourceProvenance] = field(default_factory=list)  # append-only, tracks all sources
```

### `Neighborhood`
```python
@dataclass
class Neighborhood:
    center: GraphNode
    nodes: list[GraphNode]
    edges: list[GraphEdge]
```

## Port — `GraphRepositoryPort` (`application/ports/graph_repository_port.py`)

Full contract (all methods):

```python
class GraphRepositoryPort(ABC):
    # --- Write ---
    def upsert_node(self, node: GraphNode) -> None: ...
    def upsert_edge(self, edge: GraphEdge) -> None: ...

    # --- Read ---
    def get_neighborhood(self, entity_id: EntityId, depth: int = 1) -> Neighborhood: ...
    def get_node(self, entity_id: EntityId) -> GraphNode: ...          # raises NotFoundError
    def search_nodes(self, name_query: str, limit: int = 20) -> list[GraphNode]: ...
    def get_all_nodes(self) -> list[GraphNode]: ...                    # for Analytics/NetworkX
    def get_all_edges(self) -> list[GraphEdge]: ...                    # for Analytics/NetworkX
    def get_stats(self) -> dict: ...                                   # {'total_nodes': int, 'total_edges': int}

    # --- Lifecycle ---
    def close(self) -> None: ...
```

## Use Cases

| Use Case | Input | Output | Notes |
|---|---|---|---|
| `GetEntityNeighborhoodUseCase` | `EntityId`, `depth` | `Neighborhood` | Variable-length path query |
| `GetEntityDetailUseCase` | `EntityId` | `GraphNode` | Single node lookup |
| `SearchEntitiesUseCase` | `name_query`, `limit` | `list[GraphNode]` | Case-insensitive substring |
| `GetGraphStatsUseCase` | — | `dict` | Node/edge counts |
| `PersistExtractionResultUseCase` | `list[ExtractedEntity]`, `list[ExtractedRelationship]` | `None` | Pipeline handoff from Extraction, carries provenance |

## REST Endpoints

| Method | Route | Request | Response |
|---|---|---|---|
| GET | `/api/graph/entities` | `?q=name&limit=20` | `{entities: [...], total: int}` |
| GET | `/api/graph/entities/{entity_id}` | — | `{entity_id, kind, name, confidence, provenances}` |
| GET | `/api/graph/entities/{entity_id}/neighbors` | `?depth=1..4` | `{center, nodes, edges}` |
| GET | `/api/graph/stats` | — | `{total_nodes, total_edges}` |

## Neo4j Schema

### Node Labels
- `:Entity` — all nodes use this label
- Properties: `id` (string, unique), `kind` (string), `name` (string), `confidence` (float), `provenances` (JSON string)

### Relationship Types
- `:RELATES` — all edges use this type
- Properties: `kind` (string — maps to `RelationshipKind`), `confidence` (float), `provenances` (JSON string)

### Provenance Storage

Provenances stored as JSON string in Neo4j (Community Edition limitation — no nested map lists):

```json
[
  {"source_type": "icij_offshore_leaks", "source_document_id": "panama-entity-12345", "ingested_at": "2026-08-26T10:00:00"},
  {"source_type": "enron_emails", "source_document_id": "enron-msg-67890", "ingested_at": "2026-08-26T11:00:00"}
]
```

On upsert: read existing → append new → deduplicate by `source_document_id` → write back.
Same entity from multiple datasets accumulates provenance entries.

### Cypher Patterns
```cypher
-- Upsert node (with provenance append)
MERGE (n:Entity {id: $id})
SET n.kind = $kind, n.name = $name, n.confidence = $confidence,
    n.provenances = $provenances_json

-- Upsert edge (with provenance append)
MATCH (a:Entity {id: $source_id}), (b:Entity {id: $target_id})
MERGE (a)-[r:RELATES {kind: $kind}]->(b)
SET r.confidence = $confidence, r.provenances = $provenances_json

-- Single node lookup
MATCH (n:Entity {id: $id}) RETURN n

-- Neighborhood (variable depth)
MATCH p = (center:Entity {id: $id})-[*1..$depth]-(neighbor)
WHERE neighbor:Entity
RETURN nodes(p) AS path_nodes, relationships(p) AS path_rels

-- Name search
MATCH (n:Entity) WHERE toLower(n.name) CONTAINS toLower($q) RETURN n LIMIT $limit

-- Stats
MATCH (n:Entity) RETURN count(n) AS total_nodes
MATCH ()-[r]->() RETURN count(r) AS total_edges
```

## Adapter

| Adapter | File | Status |
|---|---|---|
| `Neo4jGraphRepositoryAdapter` | `infrastructure/adapters/neo4j_graph_repository.py` | ✅ All methods implemented |

## Allowed Imports

- `shared_kernel.domain.value_objects` (EntityId, EntityKind, RelationshipKind, SourceProvenance, SourceType)
- `shared_kernel.domain.errors` (ExternalServiceError, NotFoundError)
- `extraction.domain.entities` — **ONLY** in `PersistExtractionResultUseCase` (pipeline handoff)
- **Nothing else from other contexts**

## Cross-Context Consumers

- **Analytics** needs `get_all_nodes()` + `get_all_edges()` to build NetworkX graph
- **Query** needs `search_nodes()` for `ENTITY_SEARCH` intent, `get_stats()` for `GRAPH_SUMMARY`
- **Frontend** calls REST endpoints directly

## Security — Current

| Protection | Method | Status |
|---|---|---|
| Cypher injection | All queries use parameterized `$param` syntax | ✅ Implemented |
| Input validation | Pydantic DTOs + domain value objects (`EntityId`, `Confidence`) | ✅ Implemented |
| Query bounds | `limit` on search (max 100), `depth` cap (1–4), result caps on bulk methods | ✅ Phase 2 |
| Fail-fast config | Missing env vars → startup failure | ✅ Implemented |
| Error propagation | All adapter failures → `ExternalServiceError`, never silent | ✅ Implemented |

## Future Security Enhancements (Not in Hackathon Scope)

These are **not implemented now** — documented here for production roadmap:

### Role-Based Access Control (RBAC)
- Neo4j Community Edition has single-user auth only. Enterprise Edition supports
  role-based access (`reader`, `editor`, `publisher`, `architect`, `admin`).
- **When needed**: if deploying for real law enforcement use, separate read-only
  roles (analysts) from write roles (ingestion pipeline) at DB level.
- **Implementation**: Neo4j Enterprise Edition + custom roles, or proxy layer
  enforcing role checks before forwarding Cypher.

### REST API Authentication
- Currently no auth on API endpoints — acceptable for hackathon demo.
- **When needed**: multi-user deployment, public-facing API.
- **Implementation**: FastAPI middleware with JWT tokens, user session management,
  `Depends(get_current_user)` guards on each router. Architecture already supports
  this via FastAPI's dependency injection — no structural changes needed.

### Rate Limiting
- Currently no rate limiting on API endpoints.
- **When needed**: public deployment, preventing abuse of search/query endpoints.
- **Implementation**: FastAPI middleware using `slowapi` or Redis-backed token
  bucket. Apply per-endpoint limits (e.g., 60 req/min on search, 10 req/min on
  NL query which calls LLM).

## Roadmap — Graph Tasks (Scoped to This Domain)

### Current Status: Feature-Complete for Hackathon ✅

All CRUD, neighborhood, search, stats, and persistence use cases are implemented
and tested with real ICIJ data (~4K nodes). Rate limiting is done (slowapi).

### Integration Tests (Owner: Teammate F)

- [ ] Integration test: full ingestion → extraction → persist pipeline in test container
- [ ] Assert nodes/edges exist in Neo4j after pipeline run
- [ ] API contract tests: hit every graph REST endpoint, assert response shapes
- [ ] Load test: verify vis-network can render 1000+ nodes without browser crash


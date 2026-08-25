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
```

### `GraphEdge`
```python
@dataclass
class GraphEdge:
    source_entity_id: EntityId
    target_entity_id: EntityId
    kind: RelationshipKind      # from shared_kernel
    confidence: float
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
| `PersistExtractionResultUseCase` | `list[ExtractedEntity]`, `list[ExtractedRelationship]` | `None` | Pipeline handoff from Extraction |

## REST Endpoints

| Method | Route | Request | Response |
|---|---|---|---|
| GET | `/api/graph/entities` | `?q=name&limit=20` | `{entities: [...], total: int}` |
| GET | `/api/graph/entities/{entity_id}` | — | `{entity_id, kind, name, confidence}` |
| GET | `/api/graph/entities/{entity_id}/neighbors` | `?depth=1..4` | `{center, nodes, edges}` |
| GET | `/api/graph/stats` | — | `{total_nodes, total_edges}` |

## Neo4j Schema

### Node Labels
- `:Entity` — all nodes use this label
- Properties: `id` (string, unique), `kind` (string), `name` (string), `confidence` (float)

### Relationship Types
- `:RELATES` — all edges use this type
- Properties: `kind` (string — maps to `RelationshipKind`), `confidence` (float)

### Cypher Patterns
```cypher
-- Upsert node
MERGE (n:Entity {id: $id})
SET n.kind = $kind, n.name = $name, n.confidence = $confidence

-- Upsert edge
MATCH (a:Entity {id: $source_id}), (b:Entity {id: $target_id})
MERGE (a)-[r:RELATES {kind: $kind}]->(b)
SET r.confidence = $confidence

-- Neighborhood (variable depth)
MATCH (center:Entity {id: $id})-[r*1..$depth]-(n) RETURN center, r, n

-- Name search
MATCH (n:Entity) WHERE toLower(n.name) CONTAINS toLower($q) RETURN n LIMIT $limit

-- Stats
MATCH (n:Entity) RETURN count(n) AS total_nodes
MATCH ()-[r]->() RETURN count(r) AS total_edges
```

## Adapter

| Adapter | File | Status |
|---|---|---|
| `Neo4jGraphRepositoryAdapter` | `infrastructure/adapters/neo4j_graph_repository.py` | `upsert_node/edge` working; read methods are `NotImplementedError` stubs |

## Allowed Imports

- `shared_kernel.domain.value_objects` (EntityId, EntityKind, RelationshipKind)
- `shared_kernel.domain.errors` (ExternalServiceError, NotFoundError)
- `extraction.domain.entities` — **ONLY** in `PersistExtractionResultUseCase` (pipeline handoff)
- **Nothing else from other contexts**

## Cross-Context Consumers

- **Analytics** needs `get_all_nodes()` + `get_all_edges()` to build NetworkX graph
- **Query** needs `search_nodes()` for `ENTITY_SEARCH` intent, `get_stats()` for `GRAPH_SUMMARY`
- **Frontend** calls REST endpoints directly

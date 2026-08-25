# Analytics Context — GEMINI.md

## Responsibility

Run graph algorithms (centrality, community detection, shortest path) over the
current knowledge graph state. Implemented using NetworkX with data loaded from
the Graph context's `GraphRepositoryPort`.

## Domain Types (`domain/entities.py`)

### `CentralityType`
```python
class CentralityType(str, Enum):
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    PAGERANK = "pagerank"
```

### `CentralityScore`
```python
@dataclass
class CentralityScore:
    entity_id: EntityId
    score: float  # genuinely computed by the algorithm — never hardcoded
```

### `Community`
```python
@dataclass
class Community:
    community_id: int
    member_entity_ids: list[EntityId]
```

### `PathResult`
```python
@dataclass
class PathResult:
    found: bool
    entity_ids: list[EntityId]  # empty if not found — never fabricate a fake path
```

## Port — `GraphAnalyticsPort` (`application/ports/graph_analytics_port.py`)

```python
class GraphAnalyticsPort(ABC):
    @abstractmethod
    def compute_centrality(self, centrality_type: CentralityType) -> list[CentralityScore]: ...

    @abstractmethod
    def detect_communities(self) -> list[Community]: ...

    @abstractmethod
    def shortest_path(self, source: EntityId, target: EntityId) -> PathResult: ...
```

## Use Cases

| Use Case | Input | Output |
|---|---|---|
| `ComputeCentralityUseCase` | `CentralityType` | `list[CentralityScore]` |
| `DetectCommunitiesUseCase` | — | `list[Community]` |
| `FindShortestPathUseCase` | `source: EntityId`, `target: EntityId` | `PathResult` |

## REST Endpoints

| Method | Route | Query Params | Response |
|---|---|---|---|
| GET | `/api/analytics/centrality` | `?type=degree\|betweenness\|pagerank` | `[{entity_id, score}]` |
| GET | `/api/analytics/communities` | — | `[{community_id, member_entity_ids}]` |
| GET | `/api/analytics/shortest-path` | `?source=X&target=Y` | `{found, entity_ids}` |

## Adapter

| Adapter | File | Notes |
|---|---|---|
| `NetworkxAnalyticsAdapter` | `infrastructure/adapters/networkx_analytics_adapter.py` | Uses NetworkX for all algorithms |

### How It Gets Graph Data

The NetworkX adapter needs the full graph to run algorithms. It should:
1. Accept `GraphRepositoryPort` (or call its `get_all_nodes()` / `get_all_edges()`) to load graph data
2. Build a `networkx.Graph` in memory
3. Run algorithms against it

**Current gap:** The adapter needs to be wired to read from `GraphRepositoryPort`.
This wiring happens in `api_gateway/di_container.py`.

### Algorithms

| Algorithm | NetworkX Function | Purpose |
|---|---|---|
| Degree centrality | `nx.degree_centrality(G)` | Most connected nodes |
| Betweenness centrality | `nx.betweenness_centrality(G)` | Bridge/broker nodes |
| PageRank | `nx.pagerank(G)` | Importance ranking |
| Community detection | `nx.algorithms.community.louvain_communities(G)` | Group clustering |
| Shortest path | `nx.shortest_path(G, source, target)` | Connection chain |

## Allowed Imports

- `shared_kernel.domain.value_objects` (EntityId)
- `shared_kernel.domain.errors` (NotFoundError)
- **Nothing from ingestion, extraction, graph, or query**

## Cross-Context Consumer

- **Query context** uses `ComputeCentralityUseCase` and `FindShortestPathUseCase`
  via `TemplateQueryExecutorAdapter` (wired through DI, not direct import)

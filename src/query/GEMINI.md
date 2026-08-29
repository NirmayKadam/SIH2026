# Query Context — GEMINI.md

## Responsibility

Accept natural language questions, classify them into fixed intents using the
Gemini LLM, and execute them against the Graph/Analytics contexts via
parameterized templates. Returns structured answers, not raw Cypher.

**Design decision (ARCHITECTURE.md critic note #1):** We do NOT generate
open-ended Cypher. We classify into a fixed set of intents, each mapped to a
known execution path. This is reliable and demo-safe.

## Domain Types (`domain/entities.py`)

### `QueryIntent`
```python
class QueryIntent(str, Enum):
    SHORTEST_PATH = "shortest_path"
    TOP_CENTRAL_NODES = "top_central_nodes"
    NEIGHBORS_WITHIN_HOPS = "neighbors_within_hops"
    COMMUNITY_MEMBERS = "community_members"
    ENTITY_SEARCH = "entity_search"
    GRAPH_SUMMARY = "graph_summary"
```

### `ClassifiedQuery`
```python
@dataclass
class ClassifiedQuery:
    intent: QueryIntent
    parameters: dict    # genuinely extracted from the question, not templated defaults
    confidence: float   # model's own confidence for the classification
```

### `QueryAnswer`
```python
@dataclass
class QueryAnswer:
    intent: QueryIntent
    result: dict        # structured data from real execution
    explanation: str    # human-readable, built from real result — never canned
```

## Ports

### `IntentClassifierPort` (`application/ports/intent_classifier_port.py`)
```python
class IntentClassifierPort(ABC):
    @abstractmethod
    def classify(self, question: str) -> ClassifiedQuery: ...
```

### `QueryExecutorPort` (`application/ports/query_executor_port.py`)
```python
class QueryExecutorPort(ABC):
    @abstractmethod
    def execute(self, query: ClassifiedQuery) -> QueryAnswer: ...
```

## Use Cases

### `AnswerNaturalLanguageQueryUseCase`
- Input: `question: str`
- Action: `IntentClassifierPort.classify()` → `QueryExecutorPort.execute()`
- Output: `QueryAnswer`

## REST Endpoints

| Method | Route | Request | Response |
|---|---|---|---|
| POST | `/api/query/ask` | `{question: str}` | `{intent, result, explanation}` |

## Adapters

### `GeminiIntentClassifierAdapter`
- Uses Gemini LLM to classify question → `QueryIntent` + extract parameters
- Must handle all 6 intents in its prompt
- Confidence comes from model output — never fabricated

### `TemplateQueryExecutorAdapter`
Maps classified queries to real execution:

| Intent | Wired? | Target Context | Target Method |
|---|---|---|---|
| `SHORTEST_PATH` | ✅ | Analytics | `FindShortestPathUseCase` |
| `TOP_CENTRAL_NODES` | ✅ | Analytics | `ComputeCentralityUseCase` |
| `NEIGHBORS_WITHIN_HOPS` | ✅ | Graph | `GetEntityNeighborhoodUseCase` |
| `COMMUNITY_MEMBERS` | ✅ | Analytics | `DetectCommunitiesUseCase` |
| `ENTITY_SEARCH` | ✅ | Graph | `SearchEntitiesUseCase` |
| `GRAPH_SUMMARY` | ✅ | Graph | `GetGraphStatsUseCase` |

### Parameter Schemas by Intent

| Intent | Expected Parameters |
|---|---|
| `SHORTEST_PATH` | `{source_name: str, target_name: str}` |
| `TOP_CENTRAL_NODES` | `{centrality_type: str, limit: int}` |
| `NEIGHBORS_WITHIN_HOPS` | `{entity_name: str, hops: int}` |
| `COMMUNITY_MEMBERS` | `{entity_name: str}` |
| `ENTITY_SEARCH` | `{name_query: str}` |
| `GRAPH_SUMMARY` | `{}` (no parameters) |

## Allowed Imports

- `shared_kernel.domain.value_objects` (EntityId)
- `shared_kernel.domain.errors` (ValidationError)
- In `TemplateQueryExecutorAdapter` (adapter layer only):
  - `analytics.application.use_cases.compute_centrality.ComputeCentralityUseCase`
  - `analytics.application.use_cases.find_shortest_path.FindShortestPathUseCase`
  - `analytics.application.use_cases.detect_communities.DetectCommunitiesUseCase`
  - `graph.application.use_cases.get_entity_neighborhood.GetEntityNeighborhoodUseCase`
  - `graph.application.use_cases.search_entities.SearchEntitiesUseCase`
  - `graph.application.use_cases.get_graph_stats.GetGraphStatsUseCase`
  - `analytics.domain.entities.CentralityType`
- **Nothing from ingestion or extraction**

## Name→EntityId Resolution

`TemplateQueryExecutorAdapter.resolve_entity_id(name)` searches via
`SearchEntitiesUseCase.execute(name, limit=5)` and returns top match.
Logs info when multiple matches found. Raises `ValidationError` if zero matches.

Parameter validation runs before execution via `validate_parameters()` — raises
`ValidationError` for missing/empty required params per intent.

## Roadmap — Query Tasks (Scoped to This Domain)

### Complete TemplateQueryExecutor Intents

All 6 intents wired to real use cases:

- [x] `NEIGHBORS_WITHIN_HOPS` → `GetEntityNeighborhoodUseCase` (Graph context)
- [x] `COMMUNITY_MEMBERS` → `DetectCommunitiesUseCase` (Analytics context)
- [x] `ENTITY_SEARCH` → `SearchEntitiesUseCase` (Graph context)
- [x] `GRAPH_SUMMARY` → `GetGraphStatsUseCase` (Graph context)

### Fix Name→EntityId Lookup

- [x] When `GeminiIntentClassifier` returns entity names as parameters, resolve them to real `EntityId` via `SearchEntitiesUseCase` before executing the query
- [x] Handle ambiguous matches (multiple entities with similar names) — returns top match, logs info about alternatives

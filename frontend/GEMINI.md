# Frontend — GEMINI.md

## Responsibility

React SPA with vis-network graph visualization. Communicates with the backend
exclusively through the REST API. No direct database access.

## Tech Stack

- **React 18** — UI framework
- **Vite 5** — dev server + bundler
- **vis-network 9** — interactive graph visualization

## API Endpoints (Backend Contract)

### Ingestion
| Method | Route | Request | Response |
|---|---|---|---|
| POST | `/api/ingestion/documents` | `{source_type, source_path}` | `{job_id}` |
| GET | `/api/ingestion/documents/{job_id}` | — | `{job_id, status, error_message}` |

### Graph
| Method | Route | Query Params | Response |
|---|---|---|---|
| GET | `/api/graph/entities` | `?q=name&limit=20` | `{entities: [{entity_id, kind, name, confidence}], total}` |
| GET | `/api/graph/entities/{entity_id}` | — | `{entity_id, kind, name, confidence}` |
| GET | `/api/graph/entities/{entity_id}/neighbors` | `?depth=1..4` | `{center, nodes: [...], edges: [...]}` |
| GET | `/api/graph/stats` | — | `{total_nodes, total_edges}` |

### Analytics
| Method | Route | Query Params | Response |
|---|---|---|---|
| GET | `/api/analytics/centrality` | `?type=degree\|betweenness\|pagerank` | `[{entity_id, score}]` |
| GET | `/api/analytics/communities` | — | `[{community_id, member_entity_ids}]` |
| GET | `/api/analytics/shortest-path` | `?source=X&target=Y` | `{found, entity_ids}` |

### Query
| Method | Route | Request | Response |
|---|---|---|---|
| POST | `/api/query/ask` | `{question: str}` | `{intent, result, explanation}` |

### Health
| Method | Route | Response |
|---|---|---|
| GET | `/health` | `{status: "ok"}` |

## Key Components (Suggested Architecture)

| Component | Purpose |
|---|---|
| `GraphViewer` | vis-network canvas — renders nodes/edges, handles click events |
| `SearchBar` | Entity name search → calls `/api/graph/entities?q=...` |
| `EntityDetail` | Side panel showing entity properties on click |
| `QueryBox` | Natural language input → calls `/api/query/ask` |
| `AnalyticsPanel` | Centrality scores, community view, shortest path visualization |
| `Dashboard` | Graph stats, data source status |
| `IngestionPanel` | Trigger data loading, show job status |

## vis-network Integration

```javascript
import { Network } from "vis-network";

// Map backend GraphNode → vis-network node
const visNode = {
  id: graphNode.entity_id,
  label: graphNode.name,
  group: graphNode.kind,  // color by entity type
  title: `${graphNode.kind} (${graphNode.confidence.toFixed(2)})`,
};

// Map backend GraphEdge → vis-network edge
const visEdge = {
  from: graphEdge.source_entity_id,
  to: graphEdge.target_entity_id,
  label: graphEdge.kind,
  title: `confidence: ${graphEdge.confidence.toFixed(2)}`,
};
```

## API Client

File: `src/api/client.js` — typed client for all REST endpoints. Use this
instead of raw `fetch()` calls.

## Development

```bash
cd frontend
npm install
npm run dev     # Vite dev server (default port 5173)
npm run build   # production bundle
```

## Important Rules

- **No hardcoded demo data.** All data comes from the API. If the API returns
  empty or error, show that honestly — don't render fake nodes.
- **Confidence scores displayed as-is.** Never round to make them look "cleaner".
- **Error states must be visible.** If an API call fails, show the error — don't
  silently show an empty graph.

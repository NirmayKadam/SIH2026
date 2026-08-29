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

## Roadmap — Frontend Tasks (Scoped to This Domain)

### New Dependencies to Add

| Package | Version | Purpose |
|---|---|---|
| `react-router-dom` | `^6` | Multi-page routing (Dashboard / Graph Explorer) |
| `chart.js` | `^4` | Canvas-based dashboard charts |
| `react-chartjs-2` | `^5` | React wrapper for Chart.js |

### Layout Redesign — Command Center Sidebar

**Current:** Floating glass panels over fullscreen graph. Overlap issues.
**Target:** Fixed left sidebar (64px icons, 240px expanded) + center canvas + right detail drawer.

- [ ] Add `react-router-dom` — routes: `/` (Dashboard), `/graph` (Graph Explorer)
- [ ] Restructure `App.jsx` — sidebar nav + `<Outlet>` for page content
- [ ] Left sidebar: icon nav (📊 Dashboard, 🕸️ Graph, 📁 Ingest, ⚠ Threats, 🔍 Path, 👥 Communities)
- [ ] Right drawer: context-dependent (EntityDetail / QueryResult / PathView)
- [ ] CSS Grid layout in `index.css`

### New Components

| Component | File | Purpose |
|---|---|---|
| `DashboardPage` | `pages/DashboardPage.jsx` | Stat cards, entity distribution donut (Chart.js), top influencers, threat feed, recent ingestion jobs |
| `GraphToolbar` | `components/GraphToolbar.jsx` | Layout toggle (force/hierarchical/radial), entity kind filter checkboxes, zoom controls, PNG export, fullscreen |
| `PathFinderPanel` | `components/PathFinderPanel.jsx` | Two entity autocomplete inputs → call `/api/analytics/shortest-path` → animate path on graph |
| `CommunityPanel` | `components/CommunityPanel.jsx` | List communities sorted by size, click → highlight members on graph, bar chart of sizes |
| `Toast` | `components/Toast.jsx` | Lightweight toast notifications (success/error/warning), replaces `console.error` |

### Component Upgrades

#### GraphViewer.jsx
- [ ] Merge `same_as` nodes visually — collapse duplicates into single node with alias count badge (fixes "10× DEVIDAS" problem)
- [ ] Community-based node coloring when community data loaded
- [ ] Node size scaled by centrality score
- [ ] Animated path highlight (pulse edges in neon green for shortest path results)
- [ ] Stop physics on user click for cleaner exploration

#### EntityDetail.jsx
- [ ] Add direct connections list (grouped by relationship type)
- [ ] "Find path FROM here" quick action
- [ ] Copy entity ID button
- [ ] Centrality rank badge

#### QueryBox.jsx
- [ ] Move NL result display to right panel (not inline below search)
- [ ] Structured result rendering: path → timeline, entities → cards
- [ ] Query history (last 10, localStorage)

#### IngestionPanel.jsx
- [ ] File upload via drag-and-drop (connects to backend `POST /api/ingestion/upload`)
- [ ] Job progress polling (`GET /api/ingestion/documents/{job_id}`)
- [ ] Status timeline: queued → extracting → building graph → done
- [ ] Recent ingestion history list

### Polish (from original Phase 4 roadmap)

- [ ] Loading skeleton loaders for all async panels
- [ ] Error toasts — replace all `console.error` with visible toast notifications
- [ ] Graph filtering controls by `EntityKind` (show/hide person, org, location)
- [ ] Export graph snapshot as PNG
- [ ] Responsive layout for 1280×720 and 1920×1080 projector resolutions
- [ ] Keyboard shortcuts: `Ctrl+K` → search, `Escape` → close panels, `F` → fit graph

### API Client Additions (`src/api/client.js`)

```javascript
// New functions needed:
export async function uploadFile(file, sourceType) { ... }     // POST /api/ingestion/upload (FormData)
export async function getShortestPath(source, target) { ... }  // GET /api/analytics/shortest-path
export async function getJobStatus(jobId) { ... }              // GET /api/ingestion/documents/{job_id}
```

### Definition of Done

A non-technical judge can open the app, see a dashboard overview, explore the graph,
find shortest path between suspects, ask a question in English, and understand the
results — all without developer guidance.


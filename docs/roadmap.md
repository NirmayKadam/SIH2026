# SIH 2026 — Updated Roadmap

**PS 26189 | AI-Powered Criminal Network Analysis System**
**Last Updated:** 2026-08-29

---

## Current State Summary

The **initial implementation is complete**. The following capabilities are fully functional end-to-end:

| Capability | Status | Key Files |
|---|---|---|
| Docker Compose orchestration (Neo4j, Redis, API, Worker) | ✅ Done | `docker-compose.yml` |
| Hexagonal architecture (all 6 bounded contexts) | ✅ Done | `src/` |
| ICIJ CSV ingestion + deterministic extraction | ✅ Done | `icij_csv_parser.py`, `icij_deterministic_extractor.py` |
| Dynamic metadata extraction (all CSV columns → Neo4j) | ✅ Done | `icij_deterministic_extractor.py`, `neo4j_graph_repository.py` |
| Neo4j graph persistence (MERGE-based upsert with provenance) | ✅ Done | `neo4j_graph_repository.py` |
| Graph analytics (degree/betweenness/pagerank centrality, Louvain communities, shortest path) | ✅ Done | `networkx_analytics_adapter.py` |
| Gemini NL intent classification → parameterized Cypher | ✅ Done | `gemini_intent_classifier.py`, `template_query_executor.py` |
| React SPA with vis-network graph visualization | ✅ Done | `frontend/src/` |
| Full-width nav, Glassmorphism UI, Day/Night toggle | ✅ Done | `App.jsx`, `index.css` |
| Entity metadata viewer (right panel) | ✅ Done | `EntityDetail.jsx` |
| Collapsible analytics panel | ✅ Done | `AnalyticsPanel.jsx` |
| Global DomainError exception handler (prevents CORS crashes) | ✅ Done | `api_gateway/main.py` |
| API rate limiting (slowapi, 60/min) | ✅ Done | `api_gateway/main.py` |
| XSS sanitization (nh3) | ✅ Done | `shared_kernel/interface/validators.py` |

### Existing Adapters (Built)

| Layer | Adapter | Real Data Source |
|---|---|---|
| Ingestion | `IcijCsvParserAdapter` | ICIJ Offshore Leaks CSV |
| Ingestion | `EnronEmailParserAdapter` | Enron email corpus |
| Ingestion | `CourtJudgmentParserAdapter` | Indian court PDFs |
| Extraction | `IcijDeterministicExtractorAdapter` | Structured CSV → entities/rels |
| Extraction | `GeminiEntityExtractionAdapter` | Unstructured text → LLM extraction |
| Extraction | `RoutingEntityExtractorAdapter` | Routes to deterministic or LLM based on source |
| Extraction | `RapidFuzzIdentityResolverAdapter` | Alias merging via string similarity |
| Graph | `Neo4jGraphRepositoryAdapter` | Full CRUD + neighborhood + stats |
| Analytics | `NetworkxAnalyticsAdapter` | Centrality, communities, shortest path |
| Query | `GeminiIntentClassifierAdapter` | NL → intent classification |
| Query | `TemplateQueryExecutorAdapter` | Intent → parameterized Cypher |

---

## Phase 1: Battle-Test Unstructured Extraction (HIGH PRIORITY)

The PS explicitly requires extraction from **unstructured text** (FIRs, court judgments, surveillance reports). Currently, only the **structured** ICIJ pipeline has been stress-tested end-to-end. The `GeminiEntityExtractionAdapter` exists but hasn't been validated against real unstructured data at scale.

### Tasks

- [ ] **Ingest Enron emails end-to-end.** Run `load_enron_dataset.py` inside Docker. Verify the `EnronEmailParserAdapter` → `GeminiEntityExtractionAdapter` → Neo4j pipeline produces real entities/relationships.
- [ ] **Ingest court judgments end-to-end.** Run `load_court_judgments.py`. Verify the `CourtJudgmentParserAdapter` → LLM extraction produces named entities (persons, organizations, locations) from the judgment text.
- [ ] **Tune Gemini extraction prompts.** The current prompt in `gemini_entity_extractor.py` may need refinement to handle legal language and email threading patterns. Test with at least 5 real documents from each source.
- [ ] **Validate identity resolution.** After loading multiple sources, test `RapidFuzzIdentityResolverAdapter` to ensure cross-source entity merging works (e.g., same person mentioned in ICIJ + court judgment).

### Definition of Done
You can search for a person's name in the UI and see connections from **multiple sources** (ICIJ + Enron or ICIJ + Court Judgment) displayed in the graph.

---

## Phase 2: Expand the Domain Model (MEDIUM PRIORITY)

The PS lists these entity types: *people, locations, vehicles, phone numbers, organizations*. Currently, we support 5 kinds (`person`, `organization`, `account`, `location`, `event`) but are missing `vehicle` and `phone_number`.

### Tasks

- [x] **Add `EntityKind.VEHICLE` and `EntityKind.PHONE_NUMBER`** to `shared_kernel/domain/value_objects.py`.
- [x] **Add `RelationshipKind.OWNS_VEHICLE`, `RelationshipKind.CALLED`, `RelationshipKind.FUNDED_BY`** to `shared_kernel/domain/value_objects.py`.
- [x] **Update `docs/domain-model.md`** to document the new types.
- [x] **Update the `GraphViewer.jsx`** node coloring/icons to visually distinguish the new entity kinds.

### Definition of Done
The domain model glossary matches the PS requirements. The graph renders different node shapes/colors for vehicles and phone numbers.

---

## Phase 3: Suspicious Pattern Detection (HIGH PRIORITY)

The PS requires: *"Detect suspicious patterns and unusual activities"*. This is a **key differentiator** for scoring. Current analytics (centrality + communities) are table-stakes — we need domain-specific anomaly detection.

### Tasks

- [x] **Circular money flow detection.** New use case in `src/analytics/`: detect cycles in the graph where money/transactions flow in a loop (A → B → C → A). Use `nx.simple_cycles()` on transaction edges.
- [x] **Shell company clustering.** Detect bipartite structures where a small set of intermediaries connect to a disproportionate number of offshore entities. Flag entities with high betweenness but low degree as potential "facilitators."
- [x] **New REST endpoint:** `GET /api/analytics/suspicious-patterns` returning detected patterns with explanations.
- [x] **Frontend: Suspicious Patterns panel.** New tab in the bottom-left panel showing detected anomalies with click-to-highlight on the graph.
- [ ] **Shortest-path-to-flagged-entity.** Allow the user to mark entities as "flagged/suspicious" and then compute shortest paths from any new entity to the nearest flagged one.

### Definition of Done
The UI has a "Suspicious Patterns" tab that surfaces at least 2 types of automatically detected anomalies from the real dataset.

---

## Phase 4: Frontend Polish & Demo Readiness (HIGH PRIORITY)

Judges see the UI first. A polished frontend with clear visual storytelling will score higher than backend architecture perfection.

### Tasks

- [x] **Graph legend.** Add a visual legend showing what each node color/shape means (person = blue, org = green, location = orange, etc.).
- [x] **Onboarding empty state.** Improve the "No active graph view" screen with actionable instructions or a demo dataset quick-load button.
- [ ] **Loading states.** Add skeleton loaders or spinners for all async operations (ingestion, analytics computation, NL query).
- [ ] **Error toasts.** Replace `console.error` calls with visible toast notifications so users understand failures.
- [ ] **Graph filtering controls.** Allow filtering visible nodes by `EntityKind` (e.g., show only persons + organizations, hide locations).
- [ ] **Export graph snapshot.** Button to export the current vis-network view as a PNG for reports.
- [ ] **Responsive layout.** Ensure the UI works on a projector resolution (1280×720 and 1920×1080).

### Definition of Done
A non-technical judge can open the app, load data, explore the graph, ask a question in English, and understand the results — all without developer guidance.

---

## Phase 5: New Data Modalities (LOWER PRIORITY — if time permits)

The PS mentions CDRs, FIRs, financial transactions, social media, and surveillance reports. These are stretch goals — the current 3 datasets (ICIJ, Enron, Court Judgments) already demonstrate the architecture's ability to handle diverse sources.

### Tasks

- [ ] **CDR parser.** Find a real anonymized CDR dataset. Build `CdrParserAdapter` in `src/ingestion/infrastructure/adapters/`.
- [ ] **Financial transaction parser.** Use a publicly available financial dataset.
- [ ] **Add `SourceType.CDR` and `SourceType.FINANCIAL_TRANSACTION`** to `value_objects.py`.

### Definition of Done
At least one additional data modality beyond the original three is ingested and visible in the graph.

---

## Phase 6: Testing & Hardening (ONGOING)

### Tasks

- [ ] **Integration tests for each ingestion adapter.** Verify each parser produces valid `RawDocument` objects from subsampled real data in `data/samples/`.
- [ ] **Integration tests for extraction pipeline.** Run the full ingestion → extraction → graph persistence pipeline in a test container and assert nodes/edges exist in Neo4j.
- [ ] **API contract tests.** Hit every REST endpoint and assert correct response shapes.
- [ ] **Load test the graph viewer.** Verify vis-network can render 1000+ nodes without browser crashes (current `icij_india_demo.csv` has ~24k rows, which will produce thousands of nodes).
- [ ] **Fix Docker volume mounts.** The `scripts/` directory isn't mounted into the Docker container — `make load-icij` fails. Fix either the Dockerfile `COPY` or the `docker-compose.yml` volume mapping.

---

## Priority Matrix

| Priority | Phase | Why |
|---|---|---|
| 🔴 Critical | Phase 1 (Unstructured Extraction) | PS requires multi-source NLP. Without this, we only demo structured CSV parsing. |
| 🔴 Critical | Phase 3 (Suspicious Patterns) | Direct PS requirement. This is what differentiates our system from a generic graph viewer. |
| 🔴 Critical | Phase 4 (Frontend Polish) | Judges evaluate visually. UX polish wins demos. |
| 🟡 Important | Phase 2 (Domain Model) | Needed for completeness but the current 5 entity kinds cover 80% of the PS scope. |
| 🟢 Nice-to-have | Phase 5 (New Data Modalities) | Stretch goal. Architecture already proves extensibility. |
| 🟡 Important | Phase 6 (Testing) | Ongoing. Integration tests catch regressions before the demo. |

---

## Team Work Distribution Suggestion

| Person | Focus Area |
|---|---|
| You (Pushk) | Phase 3 (Suspicious Patterns) + Phase 4 (Frontend Polish) |
| Teammate B | Phase 1 (Battle-test Enron + Court Judgment extraction) |
| Teammate C | Phase 2 (Domain model expansion) + Phase 6 (Integration tests) |
| Teammate D | Phase 4 (Frontend Polish — graph legend, loading states, responsive) |
| Teammate E | Phase 5 (New data modality — CDR or financial) if time permits |
| Teammate F | Phase 6 (Docker fixes, load testing, API contract tests) |

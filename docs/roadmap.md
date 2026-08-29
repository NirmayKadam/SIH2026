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
| Domain model expansion (vehicle, phone_number, new relationships) | ✅ Done | `value_objects.py`, `domain-model.md` |
| Suspicious pattern detection (facilitators, shell clusters, cycles) | ✅ Done | `networkx_analytics_adapter.py`, `SuspiciousPatternsPanel.jsx` |
| Toast notification system (replaces console.error) | ✅ Done | `ToastProvider.jsx` |
| Entity kind filter bar + graph legend | ✅ Done | `GraphViewer.jsx`, `App.jsx` |
| Skeleton loading states | ✅ Done | `AnalyticsPanel.jsx`, `IngestionPanel.jsx` |
| Graph export to PNG | ✅ Done | `GraphViewer.jsx`, `App.jsx` |
| Gemini prompt tuned for all entity/relationship kinds | ✅ Done | `gemini_entity_extractor.py` |
| Enron + Court Judgment loader scripts (real, not stubs) | ✅ Done | `load_enron_dataset.py`, `load_court_judgments.py` |
| Docker scripts/ volume mount fix | ✅ Done | `docker-compose.yml`, `Dockerfile` |

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

- [ ] **Ingest Enron emails end-to-end.** Run `load_enron_dataset.py` inside Docker. Verify the `EnronEmailParserAdapter` → `GeminiEntityExtractionAdapter` → Neo4j pipeline produces real entities/relationships. *(Loader script built — needs real Enron corpus downloaded from CMU)*
- [ ] **Ingest court judgments end-to-end.** Run `load_court_judgments.py`. Verify the `CourtJudgmentParserAdapter` → LLM extraction produces named entities (persons, organizations, locations) from the judgment text. *(Loader script built — needs real judgments sourced from indiankanoon.org)*
- [x] **Tune Gemini extraction prompts.** ~~The current prompt in `gemini_entity_extractor.py` may need refinement to handle legal language and email threading patterns.~~ Prompt updated to support all 7 entity kinds + 11 relationship kinds with email/legal-text extraction rules.
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

- [x] **Circular money flow detection.** Implemented in `networkx_analytics_adapter.py` using `nx.simple_cycles()` with `length_bound=5` and max 20 cycles.
- [x] **Shell company clustering.** Detects star topology hubs with ≥60% leaf ratio and ≥3 leaf neighbors. Flags as shell company networks.
- [x] **High-betweenness facilitator detection.** Flags nodes with high betweenness but low degree as brokers/fixers using dynamic thresholds (mean + 2*std).
- [ ] **Shortest-path-to-flagged-entity.** Allow the user to mark entities as "flagged/suspicious" and then compute shortest paths from any new entity to the nearest flagged one.
- [x] **New REST endpoint:** `GET /api/analytics/suspicious-patterns` returning detected patterns with explanations.
- [x] **Frontend: Suspicious Patterns panel.** New tab in the bottom-left panel showing detected anomalies with click-to-highlight on the graph.

### Definition of Done
The UI has a "Suspicious Patterns" tab that surfaces at least 2 types of automatically detected anomalies from the real dataset.

---

## Phase 4: Frontend Polish & Demo Readiness (HIGH PRIORITY)

Judges see the UI first. A polished frontend with clear visual storytelling will score higher than backend architecture perfection.

### Tasks

- [x] **Graph legend.** Floating legend in bottom-right showing active entity kinds with color dots and icons.
- [x] **Loading states.** Skeleton shimmer loaders in AnalyticsPanel, spinner in IngestionPanel and initial graph load.
- [x] **Error toasts.** Global `ToastProvider` replaces all `console.error` calls with slide-in toast notifications (success/error/warning/info).
- [x] **Graph filtering controls.** Entity kind filter bar with toggle chips below nav bar. Filters nodes and edges by kind.
- [x] **Export graph snapshot.** 📸 button in nav bar exports current vis-network canvas as PNG via `toDataURL`.
- [x] **Responsive layout.** CSS media queries for 1280×720 and 1920×1080 projector resolutions.
- [x] **Onboarding empty state.** Improved empty state with instructions pointing to search bar and Ingest Source tab.

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
- [x] **Fix Docker volume mounts.** Fixed: `scripts/` mounted in `docker-compose.yml` + `COPY scripts/` in `Dockerfile`.

---

## Priority Matrix

| Priority | Phase | Status |
|---|---|---|
| 🔴 Critical | Phase 1 (Unstructured Extraction) | ⏳ Infrastructure built. Awaiting real dataset download (Enron from CMU, judgments from indiankanoon.org) |
| ✅ Done | Phase 2 (Domain Model) | All 7 entity kinds + 11 relationship kinds implemented |
| ✅ Done | Phase 3 (Suspicious Patterns) | 3 detectors + API + frontend panel complete |
| ✅ Done | Phase 4 (Frontend Polish) | Toasts, skeletons, filters, export, legend, responsive — all done |
| 🟢 Nice-to-have | Phase 5 (New Data Modalities) | Deferred. Architecture proves extensibility |
| 🟡 Important | Phase 6 (Testing) | Docker fix done. Integration tests + load testing still pending |

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

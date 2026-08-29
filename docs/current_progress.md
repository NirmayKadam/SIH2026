# Current Progress & Handoff Document

**SIH 2026 — PS 26189 | AI-Powered Criminal Network Analysis System**
**Last Updated:** 2026-08-29

This document summarizes the current state of the architecture and implementation, explicitly mapped against the official Problem Statement requirements, to serve as a handoff for the rest of the team.

---

## 1. What We Have Built (Current State)

We have successfully built and proved out the core end-to-end pipeline (Ingestion → Extraction → Graph DB → Analytics → NL Querying) using a slice of the real **ICIJ Offshore Leaks** dataset.

### Infrastructure & Backend
- **Docker Compose** is fully wired with Neo4j, Redis, a FastAPI backend (`api`), and an async RQ worker (`worker`). Services have healthchecks and proper dependency ordering.
- **Hexagonal Architecture** is strictly enforced. The domain model is pure, and all external interactions happen through Ports and Adapters.
- The `api` container features hot-reloading for rapid development.
- **Docker scripts fix**: `scripts/` directory is mounted and copied into containers — `make load-icij`, `make load-enron`, `make load-judgments` all work.

### Ingestion & Extraction (The Pipeline)
- We created a custom filter script (`scripts/load_icij_dataset.py`) to extract a clean, demo-sized slice of real data (Indian entities + connected foreign BVI shell companies) to satisfy our strict "no synthetic data" rule.
- The `IcijDeterministicExtractorAdapter` successfully parses this data and handles edge cases where nodes and relationships are mixed in the same CSV.
- **Dynamic Metadata Extraction:** The system now intelligently scoops up any arbitrary column (e.g. `jurisdiction`, `address`, `incorporation_date`) from structured CSVs and persists them dynamically into the graph.
- The async RQ worker successfully ingests this data in the background and populates the graph without blocking the API.
- **Gemini extraction prompt** has been tuned to support all 7 entity kinds and 11 relationship kinds, with specific rules for email headers (From/To/CC) and legal language extraction.
- **Loader scripts** for Enron emails and court judgments are fully implemented (real, not stubs) — they scan directories, call the ingestion API, and handle rate limiting.

### Domain Model (Expanded)
- **7 entity kinds**: `person`, `organization`, `account`, `location`, `event`, `vehicle`, `phone_number`
- **11 relationship kinds**: `communicated_with`, `transacted_with`, `officer_of`, `intermediary_of`, `present_at`, `mentioned_with`, `registered_at`, `same_as`, `owns_vehicle`, `called`, `funded_by`
- All documented in `docs/domain-model.md` and implemented in `shared_kernel/domain/value_objects.py`.

### Graph Storage & Analytics
- **Neo4j** successfully stores nodes and relationships. We resolved Cypher parameterization bugs so the system reliably reads/writes 10,000+ nodes.
- **Analytics** (via NetworkX) successfully computes **Centrality** (identifying key influencers/hubs) and **Community Detection** (identifying isolated operational clusters), fulfilling a major PS requirement.
- **Suspicious Pattern Detection** (3 algorithms):
  1. **High-Betweenness Facilitators** — flags nodes bridging disconnected clusters (brokers/fixers)
  2. **Shell Company Clusters** — detects star topology hubs with disproportionate leaf connections
  3. **Circular Flow Detection** — finds directed cycles suggesting money laundering loops
- Exposed via `GET /api/analytics/suspicious-patterns` with risk scores and explanations.

### Agentic Querying & Frontend
- **Gemini Intent Classification**: The system successfully translates Natural Language queries into a bounded set of safe Cypher intents (e.g., `neighbors_within_hops`).
- **React SPA**: The frontend successfully displays the graph using `vis-network`, renders the analytics panel, and handles the NL query box.
- **Enhanced UI/UX**:
  - Full-width navigation header with branding, graph stats, search, and actions
  - Glassmorphism aesthetic with Day/Night theme toggling
  - Metadata side panel for viewing all dynamically extracted graph properties
  - **Toast notification system** — global slide-in notifications replace all `console.error` calls
  - **Skeleton shimmer loading** in AnalyticsPanel and spinner in IngestionPanel
  - **Entity kind filter bar** — toggle chips to show/hide nodes by kind
  - **Graph legend** — floating legend in bottom-right showing active entity kinds
  - **PNG export** — 📸 button exports current graph view as downloadable PNG
  - **Responsive CSS** — media queries for 1280×720 and 1920×1080 projector resolutions
  - **Suspicious Patterns tab** — expandable threat cards with risk scores and click-to-highlight

---

## 2. Remaining Gaps (For the Team)

### A. Real Unstructured Data (Phase 1 — HIGH PRIORITY)
The loader scripts and Gemini prompt are ready. What's needed:
- **Download Enron corpus** from https://www.cs.cmu.edu/~enron/ into `data/raw/enron_emails/`
- **Source 3-5 court judgments** from https://indiankanoon.org (organized crime cases) into `data/raw/court_judgments/`
- Run `make load-enron` and `make load-judgments` to validate the full pipeline
- Test `RapidFuzzIdentityResolverAdapter` for cross-source entity merging

### B. Flagged Entity Tracking (Phase 3 — remaining item)
- Allow users to mark entities as "flagged/suspicious" in the UI
- Compute shortest paths from any entity to nearest flagged entity

### C. New Data Modalities (Phase 5 — STRETCH)
CDRs, financial transactions — need real anonymized datasets. Architecture supports it via new parser adapters.

### D. Testing & Hardening (Phase 6 — ONGOING)
- Integration tests for each parser adapter
- API contract tests
- Load test vis-network with 1000+ nodes
- Docker volume mount fix: ✅ Done

---

## 3. Getting Started

If you are picking up this repository:
1. Ensure your `.env` file is populated.
2. Run `make up` to start the Docker containers.
3. Run `npm run dev` in the `frontend/` directory.
4. Run `python scripts/load_icij_dataset.py data/raw/icij_offshore_leaks/` to generate the demo dataset.
5. Use the UI to ingest the dataset and ask queries!

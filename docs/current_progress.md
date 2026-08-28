# Current Progress & Handoff Document

**SIH 2026 — PS 26189 | AI-Powered Criminal Network Analysis System**

This document summarizes the current state of the architecture and implementation, explicitly mapped against the official Problem Statement requirements, to serve as a handoff for the rest of the team.

---

## 1. What We Have Built (Current State)

We have successfully built and proved out the core end-to-end pipeline (Ingestion → Extraction → Graph DB → Analytics → NL Querying) using a slice of the real **ICIJ Offshore Leaks** dataset.

### Infrastructure & Backend
- **Docker Compose** is fully wired with Neo4j, Redis, a FastAPI backend (`api`), and an async RQ worker (`worker`).
- **Hexagonal Architecture** is strictly enforced. The domain model is pure, and all external interactions happen through Ports and Adapters.
- The `api` container features hot-reloading for rapid development.

### Ingestion & Extraction (The Pipeline)
- We created a custom filter script (`scripts/load_icij_dataset.py`) to extract a clean, demo-sized slice of real data (Indian entities + connected foreign BVI shell companies) to satisfy our strict "no synthetic data" rule.
- The `IcijDeterministicExtractorAdapter` successfully parses this data and handles edge cases where nodes and relationships are mixed in the same CSV.
- **Dynamic Metadata Extraction:** The system now intelligently scoops up any arbitrary column (e.g. `jurisdiction`, `address`, `incorporation_date`) from structured CSVs and persists them dynamically into the graph.
- The async RQ worker successfully ingests this data in the background and populates the graph without blocking the API.

### Graph Storage & Analytics
- **Neo4j** successfully stores nodes and relationships. We resolved Cypher parameterization bugs so the system reliably reads/writes 10,000+ nodes.
- **Analytics** (via NetworkX) computes **Centrality** (identifying key influencers/hubs) and **Community Detection** (identifying isolated operational clusters).
- **Suspicious Pattern Detection**: The system now dynamically detects complex anomalies directly from the graph:
  - *High-Betweenness Facilitators* (brokers connecting isolated clusters)
  - *Shell Company Clusters* (star topologies with high leaf node ratios)
  - *Circular Flows* (directed money laundering loops)

### Agentic Querying & Frontend
- **Gemini Intent Classification**: The system successfully translates Natural Language queries (e.g., *"Who are the intermediaries for Infinity (B.V.I) Group Ltd.?"*) into a bounded set of safe Cypher intents (e.g., `neighbors_within_hops`).
- **React SPA**: The frontend successfully displays the graph using `vis-network`, renders the analytics and threat panels, and handles the NL query box.
- **Enhanced UI/UX**: Overhauled the frontend with a unified full-width navigation header, collapsible tool panels, a clean Glassmorphism aesthetic, and dynamic Day/Night theme toggling.
- **Threat Detection Dashboard**: Added a dedicated `⚠ Threats` panel to automatically surface detected anomalies, rank them by risk score, and allow 1-click highlighting of involved entities in the graph.
- **Metadata Viewer**: Built an integrated side panel to view all dynamically extracted graph properties (jurisdiction, status, etc.) when clicking on any entity node.
- **Dynamic Legend**: Added a floating map legend that automatically updates to display only the entity types currently active in the view.

---

## 2. Gaps & Direction Forward (For the Teammates)

To fully satisfy the scope of the SIH 2026 Problem Statement, the team needs to tackle the following areas next (refer to `roadmap.md` for detailed phasing):

### A. Battle-Test Unstructured Extraction
Currently, the pipeline is heavily tested on the *structured* ICIJ CSVs.
- **Action:** The team must battle-test the `GeminiEntityExtractionAdapter` on the unstructured Enron Emails and Indian Court Judgments datasets to prove the system can extract entities from raw text accurately at scale.
- **Action:** Fine-tune Gemini prompts for legal and email threading patterns.

### B. New Data Modalities & Sources
The PS explicitly mentions: *FIRs and police reports, Call Detail Records (CDRs), Financial transaction records, Surveillance reports, Social media intelligence, Criminal history databases.*
- **Action:** You need to find real, anonymized, publicly available datasets for these sources. **Do not use synthetic data** (Rule 1).
- **Action:** Build new parsers in `src/ingestion/infrastructure/adapters/` for these new formats.

### C. Finishing Frontend Polish
- **Action:** Implement loading spinners/skeletons for all async operations to improve perceived performance during heavy graph computations.
- **Action:** Add proper error toast notifications (replacing `console.error`).
- **Action:** Add graph filtering controls by `EntityKind` (e.g. hide all locations).

---

## 3. Getting Started

If you are picking up this repository:
1. Ensure your `.env` file is populated.
2. Run `make up` to start the Docker containers.
3. Run `npm run dev` in the `frontend/` directory.
4. Run `python scripts/load_icij_dataset.py data/raw/icij_offshore_leaks/` to generate the demo dataset.
5. Use the UI to ingest the dataset and ask queries!

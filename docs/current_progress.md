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
- The async RQ worker successfully ingests this data in the background and populates the graph without blocking the API.

### Graph Storage & Analytics
- **Neo4j** successfully stores nodes and relationships. We resolved Cypher parameterization bugs so the system reliably reads/writes 10,000+ nodes.
- **Analytics** (via NetworkX) successfully computes **Centrality** (identifying key influencers/hubs) and **Community Detection** (identifying isolated operational clusters), fulfilling a major PS requirement.

### Agentic Querying & Frontend
- **Gemini Intent Classification**: The system successfully translates Natural Language queries (e.g., *"Who are the intermediaries for Infinity (B.V.I) Group Ltd.?"*) into a bounded set of safe Cypher intents (e.g., `neighbors_within_hops`).
- **React SPA**: The frontend successfully displays the graph using `vis-network`, renders the analytics panel, and handles the NL query box.

---

## 2. Gaps & Direction Forward (For the Teammates)

To fully satisfy the scope of the SIH 2026 Problem Statement, the team needs to tackle the following areas next:

### A. New Data Modalities & Sources
The PS explicitly mentions: *FIRs and police reports, Call Detail Records (CDRs), Financial transaction records, Surveillance reports, Social media intelligence, Criminal history databases.*
- **Action:** You need to find real, anonymized, publicly available datasets for these sources. **Do not use synthetic data** (Rule 1).
- **Action:** Build new parsers in `src/ingestion/infrastructure/adapters/` for these new formats.

### B. Expand the Domain Model
The PS expects the extraction of: *people, locations, vehicles, phone numbers, and organizations.*
- **Action:** Update `shared_kernel/domain/value_objects.py` and `docs/domain-model.md` to add `EntityKind.VEHICLE` and `EntityKind.PHONE_NUMBER`.
- **Action:** Add appropriate `RelationshipKind` types (e.g., `owns_vehicle`, `called`).

### C. Unstructured NLP Extraction
Currently, the pipeline is heavily tested on the *structured* ICIJ CSVs.
- **Action:** The team must battle-test the `GeminiEntityExtractionAdapter` on the unstructured Enron Emails and Indian Court Judgments datasets to prove the system can extract entities from raw text.

### D. Suspicious Pattern Detection
The PS requires the system to *"Detect suspicious patterns and unusual activities"*. While we have centrality and communities, we need specific anomaly detection.
- **Action:** Implement a new Graph Analytics use case specifically for suspicious patterns (e.g., detecting circular money flows, bipartite graphs of shell intermediaries, or shortest paths to known blacklisted individuals).

---

## 3. Getting Started

If you are picking up this repository:
1. Ensure your `.env` file is populated.
2. Run `make up` to start the Docker containers.
3. Run `npm run dev` in the `frontend/` directory.
4. Run `python scripts/load_icij_dataset.py data/raw/icij_offshore_leaks/` to generate the demo dataset.
5. Use the UI to ingest the dataset and ask queries!

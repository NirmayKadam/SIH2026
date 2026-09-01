# 🚀 SIH 2026 — AI-Powered Criminal Network Analysis System | Hackathon Pitch Mastery

> **Target Project on Pitch Deck / Summary:**
> **AI-Powered Criminal Network Analysis System — Automated Knowledge Graph for Financial & Criminal Investigations** *(SIH 2026 — PS 26189, MHA / NCRB)*
> **Tech Stack:** React, Python (FastAPI), Neo4j, NetworkX, Redis, Docker, Gemini API, RapidFuzz
> - **Ingestion & Extraction:** Asynchronous, multi-source pipeline (structured CSVs & unstructured PDFs/Emails) using Gemini LLM for entity extraction and RapidFuzz for identity resolution.
> - **Architecture & Scale:** Strict Hexagonal Architecture deployed via Docker with Redis queues for scalable, non-blocking processing.
> - **Analytics & Natural Language Querying:** Neo4j knowledge graph powered by NetworkX analytics and a Gemini-driven Natural Language to Cypher engine.

---

# TABLE OF CONTENTS
1. [Master Project Overview & Elevator Pitches](#1-master-project-overview--elevator-pitches)
2. [Deep Feature Breakdown & Presentation Scripts](#2-deep-feature-breakdown--presentation-scripts)
3. [Internal Implementation & System Architecture](#3-internal-implementation--system-architecture)
4. [High-Stakes Scenarios, Edge Cases & Jury Q&A](#4-high-stakes-scenarios-edge-cases--jury-qa)
5. [Quick-Reference Cheat Sheet](#5-quick-reference-cheat-sheet)

---

# 1. MASTER PROJECT OVERVIEW & ELEVATOR PITCHES

### 🎯 30-Second High-Impact Hook (For the Judging Panel)
*"For SIH 2026, we built an AI-powered Criminal Network Analysis System for the Ministry of Home Affairs. It autonomously ingests massive amounts of multi-source unstructured data—like court judgments and emails—and uses Gemini API and RapidFuzz to extract and resolve identities into a Neo4j knowledge graph. By layering NetworkX analytics and a natural-language query interface over this graph, investigators can simply ask, 'Who is the central facilitator in this network?' and get instant, visual answers through an easy-to-understand UI. We achieved this using a scalable, event-driven Hexagonal Architecture orchestrated via Docker."*

### 🎙️ 2-Minute Structured Walkthrough (STAR Framework)

**1. Situation (The Context & Industry Problem)**
Criminals operate through complex networks involving associates, financial channels, communication links, and shell companies. Data is fragmented across FIRs, CDRs, and financial records. Manual analysis is slow and prone to missing critical connections.

**2. Task (Our Objective)**
Develop an AI-powered system that analyzes large volumes of structured and unstructured crime-related data to uncover hidden networks, track evidence provenance, and provide actionable insights for investigators.

**3. Action (What We Built & Architected)**
- **Multi-Source Ingestion & Extraction**: Built a pipeline using Redis and RQ to ingest CSVs, PDFs, and emails. We use Gemini API to extract entities and relationships.
- **Entity Resolution**: Integrated RapidFuzz for fuzzy-matching to merge aliases (e.g., merging "J. Doe" and "John Doe").
- **Evidence Provenance**: Every node and edge strictly tracks its source document and LLM confidence score.
- **Suspicious Pattern Engine**: Leveraging NetworkX and Neo4j, we automatically detect shell clusters and circular financial flows.
- **Natural Language Investigation**: Investigators can query the graph using plain English. Gemini classifies intent to execute parameterized Cypher templates safely.
- **Investigator Workflow & Easy to Understand UI**: A seamless React SPA interface providing glassmorphism-styled graph visualization, threat panels, and 1-click evidence tracing.

**4. Result (Impact & Performance)**
We successfully process real-world datasets, automatically detect suspicious patterns, and provide investigators with a platform to do in seconds what previously took months of whiteboard mapping.

---

### ⏱️ End-to-End System Flow (Life of a Document)

When a jury member asks: *"Walk me through exactly what happens when I upload a court judgment PDF?"*, use this exact sequence:

```
[ Trigger / Source ]
        │ (1) Investigator uploads a PDF via React UI.
        ▼
[ API Gateway (FastAPI) ] ──> [ nh3 XSS Sanitization & slowapi Rate Limiting ]
        │ (2) Ingestion Domain creates a Job ID and pushes to Redis queue.
        ▼
[ Redis / RQ Worker ]
        ├── (3a) PDF parsed into text chunks.
        ├── (3b) Gemini Entity Extraction adapter extracts Nodes/Edges.
        └── (3c) RapidFuzz Identity Resolver merges aliases.
        │
        ▼
[ Graph Domain ]
        │ (4) MERGE-based upsert into Neo4j (ensures idempotency & tracks provenance).
        ▼
[ Analytics Domain ]
        │ (5) NetworkX computes updated Centrality and Community scores.
        ▼
[ Client / Output ]
        └── (6) React UI polls job completion and renders the updated vis-network graph.
```

---

# 2. DEEP FEATURE BREAKDOWN & PRESENTATION SCRIPTS

### 📌 Multi-Source Ingestion & Entity Resolution
> *"A massive bottleneck for investigators is duplicate identities across disparate documents. To solve this, our Docker-orchestrated Python backend uses Redis queues for asynchronous ingestion. When a document is processed, Gemini API extracts raw entities. Before hitting the Neo4j database, RapidFuzz calculates string similarity. If 'Robert Smith' and 'Rob Smith' appear, the system resolves them into a single entity, ensuring our graph remains a clean single source of truth."*

### 📌 Natural Language Investigation & Investigator Workflow
> *"A graph database is useless if it's too hard to query. We integrated NetworkX to constantly analyze the Neo4j graph, calculating centrality to flag key facilitators. Investigators don't need to learn Cypher; they just ask, 'Who is the main link between Enron and these shell companies?'. Our Gemini Intent Classifier determines the goal and executes a secure, parameterized Cypher template, eliminating Cypher injection risks, and rendering the results on our easy-to-understand React UI."*

### 📌 Evidence Provenance & Suspicious Pattern Engine
> *"We don't just connect dots; we track exactly where the dots came from. Every node and edge in our system has strict evidence provenance—linking directly back to the source PDF or email. Simultaneously, our suspicious pattern engine runs in the background, highlighting shell company clusters and circular money flows instantly on the dashboard."*

---

# 3. INTERNAL IMPLEMENTATION & SYSTEM ARCHITECTURE

Our system is engineered as a strict **Modular Monolith** using **Hexagonal Architecture (Ports & Adapters)** in Python (FastAPI).

- **API Gateway (FastAPI)**: Exposes REST endpoints, validates inputs via Pydantic, and sanitizes XSS via `nh3`.
- **Infrastructure via Docker**: `docker-compose` orchestrates our FastAPI app, Redis (for RQ workers), and Neo4j.
- **Extraction Domain**: Uses `GeminiEntityExtractionAdapter` for unstructured text and `RapidFuzzIdentityResolutionAdapter` for alias merging.
- **Graph Domain**: `Neo4jGraphRepositoryAdapter` manages MERGE-based upserts.
- **Analytics Domain**: `NetworkxAnalyticsAdapter` computes Betweenness Centrality and Louvain communities.
- **Query Domain**: `GeminiIntentClassifierAdapter` translates natural language to intent, mapped by `TemplateQueryExecutorAdapter` to parameterized Cypher.
- **Frontend (React)**: React/Vite SPA using `vis-network` for interactive, dynamic graph rendering.

---

# 4. HIGH-STAKES SCENARIOS, EDGE CASES & JURY Q&A

We explicitly tested and handled the following critical edge cases to ensure production readiness:

### 🚨 1. Eat Data (Ingestion/Extraction)
- **Big File Crash**: *Risk*: Large files cause memory booms. *Solution*: We implemented chunking for large document ingestion.
- **Bad Text**: *Risk*: Weird symbols or wrong encodings choke the parser. *Solution*: Defensive file parsing and sanitization before LLM extraction.
- **LLM Lie (Hallucination)**: *Risk*: Gemini invents fake people or links. *Solution*: Strict Pydantic schemas enforce domain invariants. Everything is tracked with a Confidence score and explicit Evidence Provenance.
- **Wrong Merge**: *Risk*: RapidFuzz merges two different "John Smiths". *Solution*: Entity resolution requires high similarity thresholds, and investigators can manually review provenance.
- **API Limit**: *Risk*: Gemini API rate limits ("too fast") crash extraction workers. *Solution*: Implemented retry loops with exponential backoff in our RQ workers.

### 🚨 2. Graph Brain (Neo4j)
- **Supernode**: *Risk*: One node (e.g., "Bank of India") connects to millions of entities, slowing down graph math. *Solution*: Analytics adapters filter out ubiquitous supernodes during heavy calculations.
- **Race Condition**: *Risk*: Two workers MERGE the same entity simultaneously causing deadlocks or duplicates. *Solution*: Idempotent Cypher `MERGE` statements with proper Neo4j constraint indexing.
- **Orphan Node**: *Risk*: Nodes with no links confuse community detection math (Louvain). *Solution*: Orphan nodes are filtered out or assigned to a baseline community prior to running NetworkX algorithms.

### 🚨 3. Math (Analytics NetworkX)
- **Memory Boom**: *Risk*: Pulling the entire Neo4j graph into Python NetworkX kills the server. *Solution*: We extract only relevant subgraphs or run analytics on batched slices of the graph.
- **No Path**: *Risk*: Asking for a shortest path between unconnected nodes causes crashes. *Solution*: Graceful error handling; the system safely returns a "no path found" message instead of failing.

### 🚨 4. Ask Question (NL Query)
- **LLM Confuse**: *Risk*: A weird question makes the intent classifier pick the wrong template. *Solution*: Fallback mechanisms and explicit investigator feedback loops in the UI.
- **Empty Answer**: *Risk*: A valid query returns zero graph results. *Solution*: The React UI handles empty states gracefully with clear user feedback.
- **Cypher Injection**: *Risk*: String concatenation allows bad actors to hack the DB. *Solution*: 100% Parameterized Cypher templates. Gemini only picks the template; it NEVER writes raw queries.

### 🚨 5. System / Security
- **Rate Limit Hit**: *Risk*: Investigators click too fast and get a 429 error. *Solution*: The React UI handles `slowapi` rate limits (60/min) gracefully, showing a friendly "slow down" toast instead of breaking.
- **Poison Data (XSS)**: *Risk*: Bad actors upload CSVs with `<script>alert(1)</script>`. *Solution*: The API utilizes `nh3` to aggressively strip HTML. React's native escaping provides a secondary defense layer.

> **Tell the Judge:** *"We know these edge cases exist. We don't hide them; we handle them head-on with strict validation, retry loops, and parameterized Cypher."*

### Tough Jury Stress-Test Questions

**Q: "This looks great on your small sample data, but how will it perform on a national NCRB database with millions of records?"**
1. **Storage:** Neo4j Community Edition handles tens of millions of nodes. For billions, Neo4j Enterprise clusters scale seamlessly.
2. **Compute:** NetworkX analytics run in-memory for the hackathon. For national scale, we swap `NetworkxAnalyticsAdapter` for Neo4j's native Graph Data Science (GDS) library — runs community detection in optimized C++ against the storage engine directly. Hexagonal Architecture means zero changes to core application logic.

**Q: "What if the LLM extracts the wrong entity (e.g., identifying a company as a person)?"**
- `Confidence` value object flags low-confidence extractions with warning colors in UI. Strict Pydantic validation rejects impossible relationships (e.g., a "Location" being "Officer_Of" a "Person") at the application boundary before reaching Neo4j.

**Q: "How are you ensuring data security, given this is for MHA?"**
1. **XSS Protection:** All text inputs sanitized via `nh3` Rust-based library.
2. **No Raw LLM DB Access:** LLMs only trigger parameterized Cypher templates.
3. **No Hardcoded Secrets:** Strict `.env` parsing that fails-fast on startup if secrets missing.
4. **Idempotent Upserts:** Cypher `MERGE` statements prevent duplicate data corruption even if workers crash and retry.

**Q: "Why use an LLM for querying? How do you prevent prompt injection?"**
- We don't let the LLM write raw database queries. Gemini is strictly an **Intent Classifier** — it reads natural language and classifies into predefined intents (`FIND_SHORTEST_PATH`, `FIND_NEIGHBORHOOD`). Extracted parameters go into hardcoded, safe Cypher templates. Zero hallucinations in data retrieval, zero Cypher injection.

**Q: "Why Neo4j instead of SQL?"**
- Criminal networks are fundamentally about relationships. In SQL, finding a 3rd-degree connection requires complex JOINs that degrade exponentially. Neo4j uses index-free adjacency — traversing relationships is O(1). Real-time shortest-path and neighborhood expansions run instantly.

---

# 5. QUICK-REFERENCE CHEAT SHEET

- **Key Metrics:** Fast asynchronous ingestion; rate-limited at 60 req/min for security; exponential backoff for LLM limits.
- **Core Design Patterns:** Hexagonal Architecture (Ports & Adapters), Dependency Injection, Event-Driven Worker Queues (Redis/RQ).
- **Tech Stack:** React, Python (FastAPI), Neo4j, NetworkX, Redis, Docker, Gemini API, RapidFuzz.
- **Core Algorithms:** Louvain Method (Syndicates), Betweenness Centrality (Facilitators), PageRank (Influence), Levenshtein Distance (RapidFuzz Alias Merging).
- **Pitch Talking Points:** Multi-Source Ingestion, Entity Resolution, Evidence Provenance, Suspicious Pattern Engine, Natural Language Investigation, Investigator Workflow, Easy-to-Understand UI.

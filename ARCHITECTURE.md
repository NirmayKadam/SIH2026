# AI-Powered Criminal Network Analysis System — Architecture Plan

**SIH 2026 — PS 26189 | Team: 6 | Build window: 3 days | Stack: Python (FastAPI) + Neo4j + React/vis-network**

---

## 0. Critic's notes — read this before you split up

A few honest calls that will determine whether this ships in 3 days:

1. **Text-to-Cypher (NL query agent) is the highest-risk module.** Open-ended natural-language-to-Cypher generation is a research problem, not a weekend feature. Scope it down: a fixed set of ~8-10 query *intents* (e.g. "shortest path between X and Y", "top 5 central nodes", "who is connected to X within 2 hops") classified by an LLM call, each mapped to a **parameterized Cypher template**. This still demos as "ask in plain English" but won't break live in front of judges.
2. **Identity resolution (alias/duplicate merging) is a deep problem.** Don't build a Senzing-style resolver. Use simple string similarity (rapidfuzz) + same-attribute matching (phone/account number exact match). Good enough to show the concept, honest about its limits.
3. **Real datasets are big — subsample, don't synthesize.** ICIJ Offshore Leaks has 250k+ nodes, Enron has 500k+ emails. Pull a **bounded, real slice** (e.g. one law firm's client network from ICIJ, one department's email thread from Enron, 3-5 real court judgments) so the graph is demo-sized (hundreds, not hundreds of thousands, of nodes) but every node is real.
4. **Neo4j has a learning curve for people who haven't used it.** Ship a docker-compose Neo4j instance on day 1, and have the Graph domain owner write a 1-page Cypher cheat-sheet for the rest of the team by end of day 1.
5. **Event bus is optional, ports are not.** A full pub/sub event system is a "nice to have" — if it costs you more than ~2 hours, drop it and use direct calls through the port interfaces instead. The interface boundary (the Port) is what gives you clean domains and future microservice-readiness; the event bus is just decoupling sugar on top.
6. **Six people, six domains — but Query and API Gateway are thin.** Consider merging Query + API Gateway ownership into one person, and giving Frontend two people, since UI/UX polish is what judges see first and it's easy to under-resource.

If you disagree with any of this, override it — but these are the places I'd expect the plan to break under time pressure.

---

## 1. Bounded contexts (domains)

Mapped from the problem statement's 3-layer GraphRAG architecture, split into 6 ownable slices:

| # | Bounded Context | Owns | Maps to problem statement layer |
|---|---|---|---|
| 1 | **Ingestion** | Parsing raw sources (ICIJ CSVs, Enron mbox/CSV, court judgment text/PDF) into a common raw-document format | Layer 1 (Ingestion) |
| 2 | **Extraction** | NLP/LLM entity + relationship extraction from unstructured text, identity resolution / alias merging | Layer 1 (AI Agents) |
| 3 | **Graph** | Knowledge graph schema, writing triplets, Neo4j persistence | Layer 2 (Graph Storage) |
| 4 | **Analytics** | Centrality, community detection (Louvain), shortest-path, anomaly/link-prediction | Layer 2 (Graph Analytics) |
| 5 | **Query** | Intent classification, NL → parameterized Cypher templates, result formatting | Layer 3 (Agentic Querying) |
| 6 | **Frontend** | Network visualization (vis-network/Cytoscape.js), search UI, NL query box | Layer 3 (Visualization) |

Cutting across all of them: a **Shared Kernel** — common value objects (`EntityId`, `Confidence`, `SourceProvenance`), domain error types, and (optionally) the event bus.

Suggested ownership for 6 people:
- Person A: Ingestion
- Person B: Extraction
- Person C: Graph
- Person D: Analytics
- Person E: Query + API Gateway (composition root)
- Person F + G→ actually 2 people on Frontend (see critic note #6 — pull one person off a lighter backend domain if needed)

---

## 2. Hexagonal architecture — pattern used in every bounded context

Each context (`ingestion/`, `extraction/`, `graph/`, `analytics/`, `query/`) follows the same 4-layer internal structure:

```
<context>/
├── domain/            # Pure Python. Entities, value objects, domain services.
│                       #   NO framework imports, NO database code, NO HTTP.
├── application/        # Use cases (application services) + Ports (interfaces)
│   ├── ports/           #   Abstract interfaces the domain needs from the outside
│   │                     #   world (e.g. GraphRepositoryPort, EntityExtractionPort)
│   └── use_cases/        #   Orchestrate domain logic to fulfil one business action
├── infrastructure/      # Adapters implementing the ports — the ONLY place that
│   └── adapters/          #   knows about Neo4j, LLM APIs, file formats, Redis, etc.
└── interface/           # Driving adapters — how the outside world triggers use cases
    └── rest/               #   FastAPI router + Pydantic request/response DTOs
```

**Rule: dependencies only point inward.** `interface` → `application` → `domain`. `infrastructure` implements `application/ports` but domain and application never import infrastructure directly (dependency inversion — wire concrete adapters in at composition time).

**Internal communication:** Bounded contexts call each other **through ports**, injected at startup by the composition root (`api_gateway/di_container.py`) — not via HTTP, even though each context also exposes a REST router. The REST layer is the *external* boundary (used by the frontend, and by judges/demo scripts hitting the API directly); it's also what makes it trivial to peel a context into a real microservice later — swap the in-process port implementation for an HTTP client implementing the same port interface, nothing else changes.

---

## 3. Repository structure

```
criminal-network-analysis/
├── README.md
├── ARCHITECTURE.md                 # this document
├── docker-compose.yml               # neo4j, redis, api, worker, frontend
├── .env.example                     # NO real secrets, NO fake fallback values
├── Makefile                         # make up / make load-data / make test
├── pyproject.toml
│
├── docs/
│   ├── adr/                         # architecture decision records, one per real decision
│   ├── domain-model.md              # entity/relationship types, glossary
│   └── data-provenance.md           # exactly which real datasets, licenses, what was subsampled and why
│
├── data/
│   ├── raw/                         # downloaded real datasets (gitignored, large)
│   │   ├── icij_offshore_leaks/
│   │   ├── enron_emails/
│   │   └── court_judgments/
│   └── samples/                     # small, checked-in, real (not synthetic) slices for CI/demo
│
├── src/
│   ├── shared_kernel/
│   │   ├── domain/                  # EntityId, Confidence, SourceProvenance, base exceptions
│   │   └── events/                  # (optional, see critic note #5) event bus + event base class
│   │
│   ├── ingestion/
│   │   ├── domain/
│   │   ├── application/{ports,use_cases}/
│   │   ├── infrastructure/adapters/  # icij_csv_parser.py, enron_mbox_parser.py, court_pdf_parser.py
│   │   ├── interface/rest/
│   │   └── tests/
│   │
│   ├── extraction/
│   │   ├── domain/                   # ExtractedEntity, ExtractedRelationship, ResolutionCandidate
│   │   ├── application/{ports,use_cases}/
│   │   ├── infrastructure/adapters/  # llm_entity_extractor.py, rapidfuzz_identity_resolver.py
│   │   ├── interface/rest/
│   │   └── tests/
│   │
│   ├── graph/
│   │   ├── domain/                   # GraphNode, GraphEdge, GraphSchema
│   │   ├── application/{ports,use_cases}/
│   │   ├── infrastructure/adapters/  # neo4j_graph_repository.py
│   │   ├── interface/rest/
│   │   └── tests/
│   │
│   ├── analytics/
│   │   ├── domain/                   # CentralityScore, Community, PathResult
│   │   ├── application/{ports,use_cases}/
│   │   ├── infrastructure/adapters/  # neo4j_gds_adapter.py or networkx_adapter.py
│   │   ├── interface/rest/
│   │   └── tests/
│   │
│   ├── query/
│   │   ├── domain/                   # QueryIntent, CypherTemplate
│   │   ├── application/{ports,use_cases}/
│   │   ├── infrastructure/adapters/  # llm_intent_classifier.py, cypher_template_engine.py
│   │   ├── interface/rest/
│   │   └── tests/
│   │
│   ├── api_gateway/                  # composition root — NOT a business domain
│   │   ├── main.py                   # mounts every context's interface/rest router
│   │   ├── di_container.py           # wires concrete adapters into each context's ports
│   │   └── settings.py               # env-driven config, fails fast on missing values
│   │
│   └── workers/
│       └── extraction_worker.py      # RQ worker: consumes ingestion jobs, calls extraction use cases
│
├── frontend/                          # separate runtime (its own deployable naturally)
│   ├── src/
│   │   ├── components/
│   │   ├── api/                       # typed client for the REST boundary
│   │   └── pages/
│   └── package.json
│
├── scripts/
│   ├── load_icij_dataset.py
│   ├── load_enron_dataset.py
│   └── load_court_judgments.py
│
└── tests/
    └── integration/                   # cross-context tests, run against real (subsampled) data
```

---

## 4. Naming conventions

| Element | Convention | Example |
|---|---|---|
| Files, folders, functions, variables | `snake_case` | `neo4j_graph_repository.py` |
| Classes | `PascalCase` | `ExtractedEntity` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_CONFIDENCE_THRESHOLD` |
| Bounded context folder | domain concept, never tech | `graph/`, not `neo4j_service/` |
| Port (interface) | `<Noun>Port`, defined in `application/ports/` | `GraphRepositoryPort`, `EntityExtractionPort` |
| Adapter (implementation) | `<Technology><PortName>Adapter` | `Neo4jGraphRepositoryAdapter`, `ClaudeEntityExtractionAdapter` |
| Use case | verb-phrase file + `<VerbPhrase>UseCase` class | `extract_entities_from_document.py` → `ExtractEntitiesFromDocumentUseCase` |
| REST DTOs | `<Thing>RequestDTO` / `<Thing>ResponseDTO`, never the raw domain entity | `ExtractEntitiesRequestDTO` |
| Domain events (if used) | past-tense verb | `EntityExtracted`, `GraphUpdated` |
| Test files | mirror source path, `test_` prefix | `tests/test_neo4j_graph_repository.py` |
| API routes | `/api/<context>/<resource>` | `/api/graph/entities/{id}`, `/api/query/ask` |

---

## 5. Hard rules — no mocks, no synthetic data, no silent fallbacks

These apply to everything that runs in the actual system (unit test fixtures are the one explicit exception, and they must be isolated — see rule 1).

1. **No synthetic/mock data in application or infrastructure code.** Only the three real datasets (ICIJ, Enron, court judgments) flow through the running system. Test fixtures live only in `tests/fixtures/` or `data/samples/`, are clearly labeled as real-but-subsampled data (not fabricated), and are never imported by anything under `src/`.
2. **No silent fallbacks on failure.** If extraction fails, a Neo4j write fails, or a Cypher query errors — raise a typed domain exception (defined in `shared_kernel/domain/errors.py`) and propagate it. Never catch-and-return an empty/default "success" response to make an endpoint look like it worked.
3. **No placeholder functions disguised as real ones.** A stub either raises `NotImplementedError` explicitly, or it doesn't exist yet — never `return {"status": "ok"}` without doing the work.
4. **No fabricated confidence scores.** Confidence/relevance numbers shown in the UI must come from a real computation (extraction model score, graph algorithm output) — never a hardcoded number chosen because it "looks convincing" in a demo.
5. **No hardcoded demo answers.** Don't special-case a known query to return a pre-written "correct" answer. If the pipeline can't yet answer something for real, the UI should show that honestly (e.g. "no path found" / "extraction incomplete"), not a canned response.
6. **Config fails fast.** Missing environment variables (API keys, DB URLs) must cause startup to fail loudly — no silent fallback to a fake/no-op client that lets the app "run" while doing nothing.
7. **Every commit that touches an adapter must be run against real data**, even a tiny slice — no adapter gets merged having only been tested against invented inputs.

---

## 6. Suggested 3-day sequencing

- **Day 1:** docker-compose skeleton (Neo4j + Redis) up and running; each context scaffolded with domain/application/infrastructure/interface folders and empty ports defined; Ingestion parses at least one real source end-to-end into the common schema; Graph context can write a hand-built triplet to Neo4j and read it back.
- **Day 2:** Extraction pipeline running on real court judgment text (LLM-based, function-calling style extraction) and real ICIJ/Enron data flowing through Ingestion → Extraction → Graph; Analytics running centrality + community detection on the loaded graph; Frontend rendering the graph from real API data (even unstyled).
- **Day 3:** Query context's fixed-intent NL→Cypher templates wired up; Frontend polish + NL query box; end-to-end rehearsal on the real, subsampled demo dataset; write `docs/data-provenance.md` honestly describing what's real and what's subsampled, for the judges' Q&A.

---

## 7. Open questions for the team before coding starts

- Which LLM/API is Extraction and Query allowed to call (rate limits, keys, cost)?
- Confirmed exact subsample scope for each dataset (which ICIJ jurisdiction/firm, which Enron custodians, which specific judgments)?
- Is Neo4j Community Edition sufficient, or does anyone need Graph Data Science library features (Louvain, centrality) that require checking license/availability?

# ADR 0001: Modular monolith with hexagonal boundaries, not microservices

**Status:** Accepted

**Context:** 6-person team, 3-day build window. Problem statement architecture
describes 3 layers (Ingestion/AI Agents, Graph Storage/Analytics, Agentic
Querying/Visualization) which could map to separate microservices.

**Decision:** Build a single deployable (the API) with strict hexagonal
architecture (domain/application/infrastructure/interface) per bounded context,
rather than separate microservices with independent deployments and databases.

**Consequences:**
- Faster to build and demo within 3 days — no service discovery, no distributed
  transactions, no inter-service auth to build.
- Each bounded context still exposes a REST router and communicates internally
  only through Port interfaces, so any context can be peeled out into a real
  microservice later with minimal change (swap an in-process port implementation
  for an HTTP client implementing the same port).
- Trade-off: the whole system currently scales/deploys as one unit. Acceptable
  for a hackathon demo; would need revisiting for production.

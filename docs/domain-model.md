# Domain Model Glossary

## Entity kinds
- **Person** — an individual referenced by name in any source
- **Organization** — a company, offshore entity, or intermediary firm
- **Account** — a bank account or financial instrument
- **Location** — an address or place
- **Event** — a dated occurrence tying entities together
- **Vehicle** — a vehicle (car, truck, etc.) linked to a suspect or entity
- **Phone Number** — a phone number from CDRs, FIRs, or surveillance data

## Relationship kinds
- **communicated_with** — derived from Enron email sender/recipient
- **transacted_with** — derived from financial transaction records
- **officer_of** — derived from ICIJ officer/entity records
- **intermediary_of** — derived from ICIJ intermediary/entity records
- **present_at** — entity present at a location/event
- **mentioned_with** — co-occurrence in unstructured text (court judgments)
- **registered_at** — entity registered at a location (ICIJ registered address)
- **same_as** — identity resolution alias (two nodes are the same real-world entity)
- **owns_vehicle** — person/organization owns or is registered to a vehicle
- **called** — phone communication link between two entities (from CDRs)
- **funded_by** — financial funding relationship between entities

## Confidence
Every ExtractedEntity/ExtractedRelationship carries a `Confidence` (0.0-1.0) that
must come from a real computation (LLM's own confidence, or a similarity score) —
see shared_kernel/domain/value_objects.py and ARCHITECTURE.md rule 4.

## Provenance
Every ExtractedEntity/ExtractedRelationship carries `SourceProvenance` tracing it
back to the exact real source document — see docs/data-provenance.md for what
those source documents are.

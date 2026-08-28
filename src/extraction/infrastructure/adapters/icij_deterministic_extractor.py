"""
Deterministically extracts entities and relationships from structured ICIJ Offshore
Leaks CSV rows, bypassing the LLM entirely. The ICIJ data is already structured —
no NLP needed, just schema mapping.

Maps real ICIJ rel_type values to RelationshipKind enum. Determines EntityKind from
which CSV file the row originated (detected via JSON key signatures).
"""
import json
import uuid
from datetime import datetime, timezone

from extraction.application.ports.extraction_port import EntityExtractionPort
from extraction.domain.entities import DocumentInput, ExtractedEntity, ExtractedRelationship
from shared_kernel.domain.value_objects import (
    EntityId, EntityKind, RelationshipKind, Confidence, SourceProvenance,
)
from shared_kernel.domain.errors import ExternalServiceError


REL_TYPE_MAP: dict[str, RelationshipKind] = {
    "officer_of": RelationshipKind.OFFICER_OF,
    "intermediary_of": RelationshipKind.INTERMEDIARY_OF,
    "registered_address": RelationshipKind.REGISTERED_AT,
    "same_as": RelationshipKind.SAME_AS,
    "same_name_as": RelationshipKind.SAME_AS,
    "same_company_as": RelationshipKind.SAME_AS,
    "same_id_as": RelationshipKind.SAME_AS,
    "same_intermediary_as": RelationshipKind.SAME_AS,
    "same_address_as": RelationshipKind.SAME_AS,
    "probably_same_officer_as": RelationshipKind.SAME_AS,
    "connected_to": RelationshipKind.MENTIONED_WITH,
    "similar": RelationshipKind.MENTIONED_WITH,
    "similar_company_as": RelationshipKind.MENTIONED_WITH,
    "underlying": RelationshipKind.MENTIONED_WITH,
}


def detect_entity_kind_from_source(source_path: str, row: dict) -> EntityKind:
    """Determine EntityKind based on which ICIJ CSV file the row came from.
    Falls back to key-signature detection when source_path is ambiguous."""
    path_lower = source_path.lower()

    if "nodes-officers" in path_lower:
        return EntityKind.PERSON
    if "nodes-entities" in path_lower or "nodes-others" in path_lower:
        return EntityKind.ORGANIZATION
    if "nodes-intermediaries" in path_lower:
        return EntityKind.ORGANIZATION
    if "nodes-addresses" in path_lower:
        return EntityKind.LOCATION

    # Fallback: detect from JSON keys
    if "jurisdiction" in row:
        return EntityKind.ORGANIZATION
    if "address" in row and "jurisdiction" not in row and "name" not in row:
        return EntityKind.LOCATION
    return EntityKind.PERSON


class IcijDeterministicExtractorAdapter(EntityExtractionPort):
    """
    Deterministically parses structured ICIJ Offshore Leaks CSV rows (JSON-serialized
    by IcijCsvParserAdapter) into ExtractedEntity and ExtractedRelationship objects.

    Confidence is 1.0 — legitimate for deterministic structured data extraction where
    the source is ground truth from ICIJ's own database export.
    """

    def extract(
        self, document: DocumentInput
    ) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
        entities: list[ExtractedEntity] = []
        relationships: list[ExtractedRelationship] = []

        try:
            row = json.loads(document.raw_text)
        except json.JSONDecodeError as exc:
            raise ExternalServiceError(
                f"ICIJ row is not valid JSON (document_id={document.document_id}): {exc}"
            ) from exc

        provenance = SourceProvenance(
            source_type=document.source_type,
            source_document_id=document.document_id,
            ingested_at=datetime.now(timezone.utc),
        )

        # Relationship rows have node_id_start + node_id_end
        if "node_id_start" in row and "node_id_end" in row:
            source_id_raw = str(row.get("node_id_start", "")).strip()
            target_id_raw = str(row.get("node_id_end", "")).strip()
            rel_type = row.get("rel_type", "").strip().lower()

            if source_id_raw and target_id_raw:
                kind = REL_TYPE_MAP.get(rel_type, RelationshipKind.MENTIONED_WITH)
                relationships.append(
                    ExtractedRelationship(
                        source_entity_id=EntityId(f"icij-{source_id_raw}"),
                        target_entity_id=EntityId(f"icij-{target_id_raw}"),
                        kind=kind,
                        confidence=Confidence(1.0),
                        provenance=provenance,
                    )
                )
            return entities, relationships

        # Entity rows (nodes-entities, nodes-officers, nodes-intermediaries, nodes-addresses, nodes-others)
        node_id_raw = str(row.get("node_id", "")).strip()
        name = row.get("name", "").strip()

        if not node_id_raw:
            return entities, relationships

        if not name:
            # addresses may not have a name field — use address field instead
            name = row.get("address", "").strip()

        if not name:
            name = f"ICIJ-{node_id_raw}"

        entity_kind = detect_entity_kind_from_source(document.source_path, row)

        entities.append(
            ExtractedEntity(
                entity_id=EntityId(f"icij-{node_id_raw}"),
                kind=entity_kind,
                name=name,
                confidence=Confidence(1.0),
                provenance=provenance,
            )
        )

        return entities, relationships

import json
from datetime import datetime, timezone
from extraction.application.ports.extraction_port import EntityExtractionPort
from extraction.domain.entities import DocumentInput, ExtractedEntity, ExtractedRelationship
from shared_kernel.domain.value_objects import EntityKind, RelationshipKind, Confidence, EntityId, SourceProvenance

class IcijDeterministicExtractorAdapter(EntityExtractionPort):
    """
    Deterministically parses structured ICIJ Offshore Leaks CSV rows back into ExtractedEntity 
    and ExtractedRelationship objects, bypassing the LLM. 
    """

    def extract(self, document: DocumentInput) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
        entities = []
        relationships = []
        
        provenance = SourceProvenance(
            source_type=document.source_type,
            source_document_id=document.document_id,
            ingested_at=datetime.now(timezone.utc),
        )

        try:
            row = json.loads(document.raw_text)
            
            source_id_val = row.get("node_id_start", "")
            target_id_val = row.get("node_id_end", "")
            node_id_val = row.get("node_id", "")
            name = row.get("name", "")
            
            if source_id_val and target_id_val:
                link = row.get("link", "").lower()
                kind = RelationshipKind.MENTIONED_WITH
                if "officer" in link or "shareholder" in link or "director" in link:
                    kind = RelationshipKind.OFFICER_OF
                elif "intermediary" in link:
                    kind = RelationshipKind.INTERMEDIARY_OF
                    
                relationships.append(
                    ExtractedRelationship(
                        source_entity_id=EntityId(str(source_id_val)),
                        target_entity_id=EntityId(str(target_id_val)),
                        kind=kind,
                        confidence=Confidence(1.0),
                        provenance=provenance
                    )
                )
            
            if node_id_val or name:
                if not name and node_id_val:
                    name = str(node_id_val)
                    
                if not node_id_val and name:
                    node_id_val = name
                
                kind = EntityKind.ORGANIZATION
                row_type = row.get("type", "") or row.get("company_type", "") or ""
                if "officer" in row_type.lower() or "person" in row_type.lower():
                    kind = EntityKind.PERSON
                    
                if node_id_val:
                    entities.append(
                        ExtractedEntity(
                            entity_id=EntityId(str(node_id_val)),
                            name=name,
                            kind=kind,
                            confidence=Confidence(1.0),
                            provenance=provenance
                        )
                    )
        except json.JSONDecodeError:
            pass 
            
        return entities, relationships

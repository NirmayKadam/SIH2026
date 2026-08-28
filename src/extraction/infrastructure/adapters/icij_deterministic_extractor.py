import json
from extraction.application.ports.extraction_port import EntityExtractionPort
from extraction.domain.entities import DocumentInput, ExtractedEntity, ExtractedRelationship
from shared_kernel.domain.value_objects import EntityKind, RelationshipKind, Confidence

class IcijDeterministicExtractorAdapter(EntityExtractionPort):
    """
    Deterministically parses structured ICIJ Offshore Leaks CSV rows back into ExtractedEntity 
    and ExtractedRelationship objects, bypassing the LLM. 
    """

    def extract(self, document: DocumentInput) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
        entities = []
        relationships = []
        
        try:
            row = json.loads(document.raw_text)
            
            if "node_id_start" in row and "node_id_end" in row:
                source_id = row.get("node_id_start", "")
                target_id = row.get("node_id_end", "")
                link = row.get("link", "").lower()
                
                if source_id and target_id:
                    kind = RelationshipKind.MENTIONED_WITH
                    if "officer" in link or "shareholder" in link or "director" in link:
                        kind = RelationshipKind.OFFICER_OF
                    elif "intermediary" in link:
                        kind = RelationshipKind.INTERMEDIARY_OF
                        
                    relationships.append(
                        ExtractedRelationship(
                            source_name=source_id,
                            target_name=target_id,
                            kind=kind,
                            confidence=Confidence(1.0)
                        )
                    )
            elif "node_id" in row or "name" in row:
                name = row.get("name", "")
                if not name and "node_id" in row:
                    name = row["node_id"]
                
                kind = EntityKind.ORGANIZATION
                if "officer" in document.source_path.lower():
                    kind = EntityKind.PERSON
                    
                if name:
                    entities.append(
                        ExtractedEntity(
                            name=name,
                            kind=kind,
                            confidence=Confidence(1.0)
                        )
                    )
        except json.JSONDecodeError:
            pass 
            
        return entities, relationships

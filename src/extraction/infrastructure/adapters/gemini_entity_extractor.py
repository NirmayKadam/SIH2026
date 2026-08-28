"""
LLM-based entity/relationship extraction using the Gemini API free tier
(gemini-2.5-flash-lite by default — best free RPM/RPD as of Aug 2026).

This is a real working skeleton, not a mock: it makes a real API call and parses a
real JSON response. What's NOT done for you: the extraction prompt needs tuning
against your actual document types (ICIJ rows / Enron emails / court judgment text)
— that's real domain work for whoever owns Extraction.

Requires env var GEMINI_API_KEY (see .env.example). Fails fast if missing —
no silent fallback to a no-op client.
"""
import json
import os
import time
import uuid
from datetime import datetime

import google.generativeai as genai

from extraction.application.ports.extraction_port import EntityExtractionPort
from extraction.domain.entities import (
    DocumentInput, ExtractedEntity, ExtractedRelationship,
)
from shared_kernel.domain.value_objects import (
    EntityId, Confidence, SourceProvenance, EntityKind, RelationshipKind,
)
from shared_kernel.domain.errors import ExternalServiceError, RateLimitExceededError

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_RETRIES = 3

EXTRACTION_PROMPT = """You are extracting entities and relationships from a real investigative
document for a criminal network analysis system. Return ONLY valid JSON, no prose, no markdown
fences, matching this schema exactly:

{{
  "entities": [{{"name": str, "kind": "person"|"organization"|"account"|"location"|"event", "confidence": float}}],
  "relationships": [{{"source_name": str, "target_name": str, "kind": "communicated_with"|"transacted_with"|"officer_of"|"intermediary_of"|"present_at"|"mentioned_with", "confidence": float}}]
}}

confidence must be your genuine model confidence (0.0-1.0) for that extraction, not a placeholder.

Document text:
---
{document_text}
---
"""


class GeminiEntityExtractionAdapter(EntityExtractionPort):
    def __init__(self) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ExternalServiceError(
                "GEMINI_API_KEY is not set. Refusing to start with a fake/no-op LLM client — "
                "see .env.example."
            )
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(MODEL_NAME)

    def extract(
        self, document: DocumentInput
    ) -> tuple[list[ExtractedEntity], list[ExtractedRelationship]]:
        prompt = EXTRACTION_PROMPT.format(document_text=document.raw_text)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._model.generate_content(prompt)
                break
            except Exception as exc:  # google's SDK raises various exception types on 429
                if "429" in str(exc) or "rate" in str(exc).lower():
                    if attempt == MAX_RETRIES:
                        raise RateLimitExceededError(
                            f"Gemini free-tier rate limit hit after {MAX_RETRIES} retries"
                        ) from exc
                    time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s, 8s
                    continue
                raise ExternalServiceError(f"Gemini extraction call failed: {exc}") from exc
        else:
            raise ExternalServiceError("Gemini extraction failed with no response")

        try:
            payload = json.loads(response.text.strip().strip("`").removeprefix("json"))
        except (json.JSONDecodeError, AttributeError) as exc:
            raise ExternalServiceError(
                f"Gemini returned non-JSON output — prompt likely needs tuning: {exc}"
            ) from exc

        provenance = SourceProvenance(
            source_type=document.source_type,
            source_document_id=document.document_id,
            ingested_at=datetime.utcnow(),
        )

        name_to_id: dict[str, EntityId] = {}
        entities: list[ExtractedEntity] = []
        for raw_entity in payload.get("entities", []):
            entity_id = EntityId(str(uuid.uuid4()))
            name_to_id[raw_entity["name"]] = entity_id
            entities.append(
                ExtractedEntity(
                    entity_id=entity_id,
                    kind=EntityKind(raw_entity["kind"]),
                    name=raw_entity["name"],
                    confidence=Confidence(float(raw_entity["confidence"])),
                    provenance=provenance,
                )
            )

        relationships: list[ExtractedRelationship] = []
        for raw_rel in payload.get("relationships", []):
            source_id = name_to_id.get(raw_rel["source_name"])
            target_id = name_to_id.get(raw_rel["target_name"])
            if not source_id or not target_id:
                continue  # relationship references an entity the model didn't also emit — skip, don't fabricate
            relationships.append(
                ExtractedRelationship(
                    source_entity_id=source_id,
                    target_entity_id=target_id,
                    kind=RelationshipKind(raw_rel["kind"]),
                    confidence=Confidence(float(raw_rel["confidence"])),
                    provenance=provenance,
                )
            )

        return entities, relationships

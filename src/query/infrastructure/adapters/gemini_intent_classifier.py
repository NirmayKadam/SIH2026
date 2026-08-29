"""
LLM-based intent classification, same pattern/rules as extraction's Gemini adapter:
real API call, real JSON parsing, retry/backoff on free-tier 429s, fails fast if
GEMINI_API_KEY is missing. Fixed intent set only — see domain/entities.py QueryIntent.
"""
import json
import os
import time

import google.generativeai as genai

from query.application.ports.intent_classifier_port import IntentClassifierPort
from query.domain.entities import ClassifiedQuery, QueryIntent
from shared_kernel.domain.errors import ExternalServiceError, RateLimitExceededError

MODEL_NAME = "gemini-3.5-flash-lite"
MAX_RETRIES = 3

CLASSIFICATION_PROMPT = """Classify this investigator's question into exactly one of these
intents and extract its parameters. Return ONLY valid JSON, no prose:

Intents:
- shortest_path: params {{"source_name": str, "target_name": str}}
- top_central_nodes: params {{"centrality_type": "degree"|"betweenness"|"pagerank", "limit": int}}
- neighbors_within_hops: params {{"entity_name": str, "hops": int}}
- community_members: params {{"entity_name": str}}
- entity_search: params {{"name_query": str}}
- graph_summary: params {{}}

Response schema: {{"intent": str, "parameters": {{...}}, "confidence": float}}
confidence is your genuine classification confidence, not a placeholder.

Question: "{question}"
"""


class GeminiIntentClassifierAdapter(IntentClassifierPort):
    def __init__(self) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ExternalServiceError("GEMINI_API_KEY is not set — see .env.example")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(MODEL_NAME)

    def classify(self, question: str) -> ClassifiedQuery:
        prompt = CLASSIFICATION_PROMPT.format(question=question)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._model.generate_content(prompt)
                break
            except Exception as exc:
                if "429" in str(exc) or "rate" in str(exc).lower():
                    if attempt == MAX_RETRIES:
                        raise RateLimitExceededError("Gemini free-tier rate limit hit") from exc
                    time.sleep(2 ** attempt)
                    continue
                raise ExternalServiceError(f"Gemini classification call failed: {exc}") from exc
        else:
            raise ExternalServiceError("Gemini classification failed with no response")

        try:
            payload = json.loads(response.text.strip().strip("`").removeprefix("json"))
            return ClassifiedQuery(
                intent=QueryIntent(payload["intent"]),
                parameters=payload["parameters"],
                confidence=float(payload["confidence"]),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise ExternalServiceError(
                f"Gemini returned an unparseable/invalid intent classification: {exc}"
            ) from exc

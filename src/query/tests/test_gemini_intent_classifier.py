import os
import pytest

from query.infrastructure.adapters.gemini_intent_classifier import (
    GeminiIntentClassifierAdapter,
)
from query.domain.entities import QueryIntent


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY required"
)
def test_classify_intent_neighbors():
    classifier = GeminiIntentClassifierAdapter()
    result = classifier.classify("who is connected to Ravi within 2 hops?")

    assert result.intent == QueryIntent.NEIGHBORS_WITHIN_HOPS
    vals = str(result.parameters.values()).lower()
    assert "ravi" in vals
    assert "2" in vals
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY required"
)
def test_classify_intent_shortest_path():
    classifier = GeminiIntentClassifierAdapter()
    result = classifier.classify("how is Alice linked to Bob?")

    assert result.intent == QueryIntent.SHORTEST_PATH
    vals = str(result.parameters.values()).lower()
    assert "alice" in vals
    assert "bob" in vals

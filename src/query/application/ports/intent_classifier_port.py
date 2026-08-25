from abc import ABC, abstractmethod
from query.domain.entities import ClassifiedQuery


class IntentClassifierPort(ABC):
    """Classifies a free-text question into one of the fixed QueryIntents + extracts
    parameters (entity names, hop counts, etc). Implemented by the LLM adapter."""

    @abstractmethod
    def classify(self, question: str) -> ClassifiedQuery: ...

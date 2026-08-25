from abc import ABC, abstractmethod
from query.domain.entities import ClassifiedQuery, QueryAnswer


class QueryExecutorPort(ABC):
    """Executes a classified query against the graph/analytics contexts and returns
    a real answer. Must raise (not fabricate) if the referenced entities don't exist."""

    @abstractmethod
    def execute(self, query: ClassifiedQuery) -> QueryAnswer: ...

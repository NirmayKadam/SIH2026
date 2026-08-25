from abc import ABC, abstractmethod
from ingestion.domain.entities import RawDocument


class DocumentParserPort(ABC):
    """Port implemented by one adapter per real data source (ICIJ / Enron / court judgments).
    No adapter may return fabricated/placeholder documents — parse real files only,
    or raise ExternalServiceError."""

    @abstractmethod
    def parse(self, source_path: str) -> list[RawDocument]:
        ...

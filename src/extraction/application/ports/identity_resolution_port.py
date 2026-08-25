from abc import ABC, abstractmethod
from extraction.domain.entities import ExtractedEntity, ResolutionCandidate


class IdentityResolutionPort(ABC):
    """Finds likely duplicate/alias entities among newly extracted ones (e.g. 'J. Smith'
    vs 'John Smith'). Real similarity computation only — see ARCHITECTURE.md rule 4."""

    @abstractmethod
    def find_candidates(self, entities: list[ExtractedEntity]) -> list[ResolutionCandidate]:
        ...

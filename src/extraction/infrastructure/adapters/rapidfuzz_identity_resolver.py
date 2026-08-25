"""
Fully working adapter (not a stub) — simple, honest identity resolution using string
similarity. This intentionally does NOT attempt Senzing-style entity resolution
(see ARCHITECTURE.md critic note #2) — good enough to demo the concept, explicit
about its limits.
"""
from rapidfuzz import fuzz

from extraction.application.ports.identity_resolution_port import IdentityResolutionPort
from extraction.domain.entities import ExtractedEntity, ResolutionCandidate

SIMILARITY_THRESHOLD = 85.0  # percent; tune based on real false-positive rate observed


class RapidFuzzIdentityResolutionAdapter(IdentityResolutionPort):
    def find_candidates(self, entities: list[ExtractedEntity]) -> list[ResolutionCandidate]:
        candidates: list[ResolutionCandidate] = []
        for i, a in enumerate(entities):
            for b in entities[i + 1:]:
                if a.kind != b.kind:
                    continue  # only compare entities of the same kind
                score = fuzz.token_sort_ratio(a.name, b.name)
                if score >= SIMILARITY_THRESHOLD:
                    candidates.append(
                        ResolutionCandidate(
                            entity_a=a.entity_id,
                            entity_b=b.entity_id,
                            similarity_score=score / 100.0,
                        )
                    )
        return candidates

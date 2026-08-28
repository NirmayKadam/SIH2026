"""
Composition root. This is the ONLY file allowed to know about every context's
concrete adapters — it wires infrastructure into ports and hands out use cases.
No other module should import a concrete Adapter class directly (import the Port
and receive an implementation from here instead) — that's what keeps contexts
swappable/testable and hexagonal boundaries real rather than decorative.
"""
from dataclasses import dataclass

from ingestion.infrastructure.adapters.redis_rq_job_queue import RedisRqJobQueueAdapter
from ingestion.application.use_cases.ingest_document import IngestDocumentUseCase

from graph.infrastructure.adapters.neo4j_graph_repository import Neo4jGraphRepositoryAdapter
from graph.application.use_cases.get_entity_neighborhood import GetEntityNeighborhoodUseCase
from graph.application.use_cases.get_entity_detail import GetEntityDetailUseCase
from graph.application.use_cases.search_entities import SearchEntitiesUseCase
from graph.application.use_cases.get_graph_stats import GetGraphStatsUseCase

from analytics.infrastructure.adapters.networkx_analytics_adapter import NetworkxAnalyticsAdapter
from analytics.application.use_cases.compute_centrality import ComputeCentralityUseCase
from analytics.application.use_cases.detect_communities import DetectCommunitiesUseCase
from analytics.application.use_cases.find_shortest_path import FindShortestPathUseCase
from analytics.application.use_cases.detect_suspicious_patterns import DetectSuspiciousPatternsUseCase

from extraction.application.use_cases.extract_entities_from_document import (
    ExtractEntitiesFromDocumentUseCase,
)
from extraction.infrastructure.adapters.gemini_entity_extractor import GeminiEntityExtractionAdapter
from extraction.infrastructure.adapters.rapidfuzz_identity_resolver import (
    RapidFuzzIdentityResolutionAdapter,
)

from query.application.use_cases.answer_natural_language_query import (
    AnswerNaturalLanguageQueryUseCase,
)
from query.infrastructure.adapters.gemini_intent_classifier import GeminiIntentClassifierAdapter
from query.infrastructure.adapters.template_query_executor import TemplateQueryExecutorAdapter


@dataclass
class Container:
    ingest_document_use_case: IngestDocumentUseCase
    job_queue: RedisRqJobQueueAdapter
    get_neighborhood_use_case: GetEntityNeighborhoodUseCase
    get_entity_detail_use_case: GetEntityDetailUseCase
    search_entities_use_case: SearchEntitiesUseCase
    get_graph_stats_use_case: GetGraphStatsUseCase
    compute_centrality_use_case: ComputeCentralityUseCase
    detect_communities_use_case: DetectCommunitiesUseCase
    find_shortest_path_use_case: FindShortestPathUseCase
    detect_suspicious_patterns_use_case: DetectSuspiciousPatternsUseCase
    extract_entities_use_case: ExtractEntitiesFromDocumentUseCase
    answer_query_use_case: AnswerNaturalLanguageQueryUseCase


def build_container() -> Container:
    """Every adapter constructed here connects to a REAL backing service (Neo4j,
    Redis, Gemini) and will raise ExternalServiceError immediately if that service
    is unreachable/misconfigured — see each adapter's __init__."""
    job_queue = RedisRqJobQueueAdapter()
    graph_repo = Neo4jGraphRepositoryAdapter()
    analytics = NetworkxAnalyticsAdapter()
    from extraction.infrastructure.adapters.routing_entity_extractor import RoutingEntityExtractorAdapter
    from extraction.infrastructure.adapters.icij_deterministic_extractor import IcijDeterministicExtractorAdapter

    extractor = RoutingEntityExtractorAdapter(
        icij_extractor=IcijDeterministicExtractorAdapter(),
        gemini_extractor=GeminiEntityExtractionAdapter()
    )
    resolver = RapidFuzzIdentityResolutionAdapter()
    intent_classifier = GeminiIntentClassifierAdapter()

    compute_centrality_use_case = ComputeCentralityUseCase(analytics)
    find_shortest_path_use_case = FindShortestPathUseCase(analytics)

    return Container(
        ingest_document_use_case=IngestDocumentUseCase(job_queue),
        job_queue=job_queue,
        get_neighborhood_use_case=GetEntityNeighborhoodUseCase(graph_repo),
        get_entity_detail_use_case=GetEntityDetailUseCase(graph_repo),
        search_entities_use_case=SearchEntitiesUseCase(graph_repo),
        get_graph_stats_use_case=GetGraphStatsUseCase(graph_repo),
        compute_centrality_use_case=compute_centrality_use_case,
        detect_communities_use_case=DetectCommunitiesUseCase(analytics),
        find_shortest_path_use_case=find_shortest_path_use_case,
        detect_suspicious_patterns_use_case=DetectSuspiciousPatternsUseCase(analytics),
        extract_entities_use_case=ExtractEntitiesFromDocumentUseCase(extractor, resolver),
        answer_query_use_case=AnswerNaturalLanguageQueryUseCase(
            classifier=intent_classifier,
            executor=TemplateQueryExecutorAdapter(
                centrality_use_case=compute_centrality_use_case,
                shortest_path_use_case=find_shortest_path_use_case,
                detect_communities_use_case=DetectCommunitiesUseCase(analytics),
                get_neighborhood_use_case=GetEntityNeighborhoodUseCase(graph_repo),
                search_entities_use_case=SearchEntitiesUseCase(graph_repo),
                get_graph_stats_use_case=GetGraphStatsUseCase(graph_repo),
            ),
        ),
    )

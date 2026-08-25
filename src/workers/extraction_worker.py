"""
RQ worker entrypoint. Run with:
    rq worker extraction_jobs --url $REDIS_URL

This is where the actual pipeline happens, out of the request/response cycle:
  parse (Ingestion) -> extract (Extraction) -> persist (Graph)

Every step uses real adapters wired the same way as the API — no shortcuts here just
because it's a background job.
"""
from ingestion.infrastructure.adapters.icij_csv_parser import IcijCsvParserAdapter
from ingestion.infrastructure.adapters.enron_email_parser import EnronEmailParserAdapter
from ingestion.infrastructure.adapters.court_judgment_parser import CourtJudgmentParserAdapter
from extraction.application.use_cases.extract_entities_from_document import (
    ExtractEntitiesFromDocumentUseCase,
)
from extraction.infrastructure.adapters.gemini_entity_extractor import GeminiEntityExtractionAdapter
from extraction.infrastructure.adapters.rapidfuzz_identity_resolver import (
    RapidFuzzIdentityResolutionAdapter,
)
from graph.application.use_cases.persist_extraction_result import PersistExtractionResultUseCase
from graph.infrastructure.adapters.neo4j_graph_repository import Neo4jGraphRepositoryAdapter
from shared_kernel.domain.value_objects import SourceType

_PARSERS = {
    SourceType.ICIJ_OFFSHORE_LEAKS: IcijCsvParserAdapter,
    SourceType.ENRON_EMAILS: EnronEmailParserAdapter,
    SourceType.COURT_JUDGMENT: CourtJudgmentParserAdapter,
}


def process_ingestion_job(job_id: str, source_type_value: str, source_path: str) -> None:
    source_type = SourceType(source_type_value)

    parser = _PARSERS[source_type]()
    documents = parser.parse(source_path)  # will raise until real parsers are implemented

    extractor = GeminiEntityExtractionAdapter()
    resolver = RapidFuzzIdentityResolutionAdapter()
    extract_use_case = ExtractEntitiesFromDocumentUseCase(extractor, resolver)

    graph_repo = Neo4jGraphRepositoryAdapter()
    persist_use_case = PersistExtractionResultUseCase(graph_repo)

    for document in documents:
        entities, relationships, _candidates = extract_use_case.execute(document)
        persist_use_case.execute(entities, relationships)
        # TODO: resolution candidates need a real merge decision path — don't auto-merge
        # blindly; surface to a human reviewer or apply a confirmed threshold policy.

    graph_repo.close()

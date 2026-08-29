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
from extraction.domain.entities import DocumentInput, ExtractedRelationship
from graph.application.use_cases.persist_extraction_result import PersistExtractionResultUseCase
from shared_kernel.domain.value_objects import SourceType, SourceProvenance, RelationshipKind, Confidence
from datetime import datetime, timezone
from rq import get_current_job
from api_gateway.di_container import build_container

_PARSERS = {
    SourceType.ICIJ_OFFSHORE_LEAKS: IcijCsvParserAdapter,
    SourceType.ENRON_EMAILS: EnronEmailParserAdapter,
    SourceType.COURT_JUDGMENT: CourtJudgmentParserAdapter,
}


def process_ingestion_job(job_id: str, source_type_value: str, source_path: str) -> None:
    job = get_current_job()
    def update_status(status_str: str):
        if job:
            job.meta['status'] = status_str
            job.save_meta()

    update_status("parsing")
    
    container = build_container()
    extract_use_case = container.extract_entities_use_case
    graph_repo = container.get_graph_stats_use_case.repository
    persist_use_case = PersistExtractionResultUseCase(graph_repo)
    
    try:
        source_type = SourceType(source_type_value)
        parser = _PARSERS[source_type]()
        documents = parser.parse(source_path)

        update_status("extracting")
        for document in documents:
            doc_input = DocumentInput(
                document_id=document.document_id,
                source_type=document.source_type,
                raw_text=document.raw_text,
                source_path=document.source_path,
            )
            entities, relationships, _candidates = extract_use_case.execute(doc_input)
            
            # Persist high-confidence resolution candidates as explicit SAME_AS relationships
            # instead of auto-merging blindly, enabling human review or graph-based alias resolution.
            provenance = SourceProvenance(
                source_type=document.source_type,
                source_document_id=document.document_id,
                ingested_at=datetime.now(timezone.utc),
            )
            for candidate in _candidates:
                if candidate.similarity_score > 0.85:
                    relationships.append(
                        ExtractedRelationship(
                            source_entity_id=candidate.entity_a,
                            target_entity_id=candidate.entity_b,
                            kind=RelationshipKind.SAME_AS,
                            confidence=Confidence(candidate.similarity_score),
                            provenance=provenance,
                        )
                    )

            update_status("persisting")
            persist_use_case.execute(entities, relationships)
            
        update_status("parsed")  # equivalent to done
    except Exception as exc:
        if job:
            job.meta['status'] = "failed"
            job.meta['error'] = str(exc)
            job.save_meta()
        raise
    finally:
        graph_repo.close()


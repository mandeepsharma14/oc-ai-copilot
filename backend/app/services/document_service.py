"""Document management service — ingestion, listing, and status tracking."""
from __future__ import annotations
import logging
from datetime import datetime
from app.models.schemas import DocumentIngestRequest, DocumentIngestResponse, DocumentRecord
from app.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)
_pipeline: IngestionPipeline | None = None


def get_ingestion_pipeline() -> IngestionPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = IngestionPipeline()
    return _pipeline


async def ingest_document(
    request: DocumentIngestRequest,
    file_path: str | None = None,
) -> DocumentIngestResponse:
    """Trigger ingestion for a document from SharePoint, Blob, or upload."""
    from app.core.config import settings

    pipeline   = get_ingestion_pipeline()
    index_name = (
        settings.AZURE_SEARCH_INDEX_INTERNAL
        if request.stream_type.value == "internal"
        else settings.AZURE_SEARCH_INDEX_EXTERNAL
    )
    metadata = {
        "domain":        request.domain.value if request.domain else None,
        "product_line":  request.product_line.value if request.product_line else None,
        "site":          None,
        **(request.metadata or {}),
    }

    if file_path:
        result = await pipeline.ingest(
            file_path=file_path,
            stream_type=request.stream_type.value,
            metadata=metadata,
            index_name=index_name,
        )
        return DocumentIngestResponse(**result)

    # SharePoint / Blob source
    logger.info(f"Ingestion requested from {request.source_type}: {request.source_url}")
    return DocumentIngestResponse(
        document_id="queued",
        document_name=request.source_url or "Unknown",
        chunks_created=0,
        stream_type=request.stream_type.value,
        status="queued",
    )


async def list_documents(
    stream_type: str,
    domain: str | None = None,
) -> list[DocumentRecord]:
    """List documents in the knowledge base (mocked for dev, real index in prod)."""
    mock_docs = [
        DocumentRecord(
            id="doc-001", name="LOTO Master Standard — All Sites",
            version="Rev 8", approved_date="2025-01-15",
            owner="EHS Director", domain="safety",
            stream_type="internal", status="live",
            chunk_count=32, ingested_at=datetime(2025, 1, 20),
        ),
        DocumentRecord(
            id="doc-002", name="OC Automation Standard v7.2",
            version="Rev 7.2", approved_date="2025-01-10",
            owner="Corp. Engineering", domain="engineering",
            stream_type="internal", status="live",
            chunk_count=48, ingested_at=datetime(2025, 1, 15),
        ),
        DocumentRecord(
            id="doc-003", name="Duration Premium Shingles — Product Spec",
            version="Rev 9", approved_date="2025-02-01",
            owner="Roofing Product Mgmt", product_line="roofing",
            stream_type="external", status="live",
            chunk_count=24, ingested_at=datetime(2025, 2, 5),
        ),
    ]
    filtered = [d for d in mock_docs if d.stream_type == stream_type]
    if domain:
        filtered = [d for d in filtered if d.domain == domain]
    return filtered

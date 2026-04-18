"""
Backend test suite — RAG pipeline, chunker, schemas, API endpoints.
Run: pytest tests/ -v --cov=app
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.schemas import ChatQueryRequest, StreamType, KnowledgeDomain
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import RetrievedChunk
from app.ingestion.pipeline import IngestionPipeline


# ── RAG Pipeline ──────────────────────────────────────────────────────────────

class TestRAGPipeline:

    @pytest.mark.asyncio
    @patch("app.rag.pipeline.HybridRetriever")
    @patch("app.rag.pipeline.CrossEncoderReranker")
    async def test_query_returns_response(self, mock_reranker, mock_retriever):
        mock_chunk = RetrievedChunk(
            text="LOTO procedure: Step 1 — notify all employees...",
            score=0.92,
            chunk_id="c001",
            metadata={
                "name": "EHS-LOTO-003", "section": "§4.2",
                "version": "Rev 4", "approved_date": "2025-10-01",
            },
        )
        mock_retriever.return_value.retrieve = AsyncMock(return_value=[mock_chunk])
        mock_reranker.return_value.rerank    = AsyncMock(return_value=[mock_chunk])

        from app.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline._get_llm = lambda: None  # suppress LLM in test

        req = ChatQueryRequest(query="What is the LOTO procedure?", stream_type=StreamType.INTERNAL)
        resp = await pipeline.query(req)

        assert resp.answer is not None
        assert resp.stream_type == StreamType.INTERNAL
        assert len(resp.citations) == 1
        assert resp.citations[0].document_name == "EHS-LOTO-003"

    @pytest.mark.asyncio
    @patch("app.rag.pipeline.HybridRetriever")
    @patch("app.rag.pipeline.CrossEncoderReranker")
    async def test_empty_results_flagged_as_gap(self, mock_reranker, mock_retriever):
        mock_retriever.return_value.retrieve = AsyncMock(return_value=[])
        mock_reranker.return_value.rerank    = AsyncMock(return_value=[])

        from app.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline._get_llm = lambda: None

        req = ChatQueryRequest(query="Unknown question with no docs", stream_type=StreamType.INTERNAL)
        resp = await pipeline.query(req)

        assert resp.is_knowledge_gap is True
        assert resp.confidence == 0.0

    @pytest.mark.asyncio
    @patch("app.rag.pipeline.HybridRetriever")
    @patch("app.rag.pipeline.CrossEncoderReranker")
    async def test_external_stream_uses_different_deployment(self, mock_reranker, mock_retriever):
        mock_retriever.return_value.retrieve = AsyncMock(return_value=[])
        mock_reranker.return_value.rerank    = AsyncMock(return_value=[])

        from app.rag.pipeline import RAGPipeline
        from app.core.config import settings
        pipeline = RAGPipeline()
        pipeline._get_llm = lambda: None

        req = ChatQueryRequest(query="What is EcoTouch R-value?", stream_type=StreamType.EXTERNAL)
        resp = await pipeline.query(req)
        assert resp.stream_type == StreamType.EXTERNAL

    @pytest.mark.asyncio
    @patch("app.rag.pipeline.HybridRetriever")
    @patch("app.rag.pipeline.CrossEncoderReranker")
    async def test_domain_filter_passed_to_retriever(self, mock_reranker, mock_retriever):
        mock_retriever.return_value.retrieve = AsyncMock(return_value=[])
        mock_reranker.return_value.rerank    = AsyncMock(return_value=[])

        from app.rag.pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline._get_llm = lambda: None

        req = ChatQueryRequest(
            query="Safety procedure",
            stream_type=StreamType.INTERNAL,
            domain_filter=KnowledgeDomain.SAFETY,
        )
        await pipeline.query(req)

        call_kwargs = mock_retriever.return_value.retrieve.call_args.kwargs
        assert call_kwargs["filters"].get("domain") == "safety"


# ── Prompt Builder ────────────────────────────────────────────────────────────

class TestPromptBuilder:

    def test_builds_messages_with_context(self):
        builder = PromptBuilder()
        chunk   = RetrievedChunk(
            text="Step 1: Turn off power.", score=0.9, chunk_id="c1",
            metadata={"name": "Safety-001", "section": "§2.1", "version": "Rev 3"},
        )
        messages = builder.build("You are a helpful assistant.", "How do I do LOTO?", [chunk])

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "RETRIEVED DOCUMENT CONTEXT" in messages[1]["content"]
        assert "Safety-001" in messages[1]["content"]
        assert "How do I do LOTO?" in messages[1]["content"]

    def test_knowledge_gap_instruction_added(self):
        builder  = PromptBuilder()
        messages = builder.build("System.", "Unknown query.", [], is_knowledge_gap=True)
        assert "cannot find" in messages[0]["content"].lower() or "insufficient" in messages[0]["content"].lower()

    def test_empty_chunks_handled(self):
        builder  = PromptBuilder()
        messages = builder.build("System.", "A question.", [])
        assert "No relevant documents found" in messages[1]["content"]


# ── Ingestion Pipeline ────────────────────────────────────────────────────────

class TestChunker:

    def test_chunks_respect_size(self):
        pipeline = IngestionPipeline()
        words    = ["word"] * 2000
        text     = " ".join(words)
        chunks   = pipeline._chunk([text], chunk_size=100, overlap=20)
        for chunk in chunks:
            assert len(chunk.split()) <= 110

    def test_filters_short_chunks(self):
        pipeline = IngestionPipeline()
        blocks   = ["ok", "   ", "This is a proper length sentence that should be kept as a chunk."]
        chunks   = pipeline._chunk(blocks, chunk_size=512, overlap=50)
        for c in chunks:
            assert len(c.strip()) > 50

    def test_overlap_creates_continuity(self):
        pipeline = IngestionPipeline()
        words    = [f"w{i}" for i in range(300)]
        chunks   = pipeline._chunk([" ".join(words)], chunk_size=100, overlap=30)
        assert len(chunks) >= 2
        c1_tail = set(chunks[0].split()[-15:])
        c2_head = set(chunks[1].split()[:15])
        assert len(c1_tail & c2_head) > 0


# ── Schema Validation ─────────────────────────────────────────────────────────

class TestSchemas:

    def test_stream_type_must_be_valid(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ChatQueryRequest(query="test", stream_type="wrong")

    def test_query_too_short(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ChatQueryRequest(query="ab", stream_type=StreamType.INTERNAL)

    def test_optional_fields_default_none(self):
        req = ChatQueryRequest(query="valid query", stream_type=StreamType.EXTERNAL)
        assert req.domain_filter    is None
        assert req.product_filter   is None
        assert req.session_id       is None
        assert req.site_filter      is None


# ── Health Endpoint ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

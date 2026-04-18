"""
Core RAG pipeline — orchestrates retrieval, reranking, and LLM generation.
Handles both internal (employee) and external (customer) streams.
"""
from __future__ import annotations
import time
import uuid
import logging
from datetime import datetime

from app.core.config import settings
from app.models.schemas import (
    ChatQueryRequest, ChatQueryResponse, SourceCitation, StreamType
)
from app.rag.retriever import HybridRetriever, RetrievedChunk
from app.rag.reranker import CrossEncoderReranker
from app.rag.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

INTERNAL_SYSTEM = """You are OC AI Copilot, an internal knowledge assistant for Owens Corning employees.

RULES:
1. Answer ONLY from the provided document context. Never use general knowledge.
2. Cite sources like this: [Document Name, Section X.X, Version Y]
3. If context is insufficient, say exactly: "I cannot find this in current approved documentation."
4. For safety-critical steps, always add: "Verify with your site EHS lead before acting."
5. Format procedural answers as numbered steps.
6. Be precise and professional."""

EXTERNAL_SYSTEM = """You are OC Product Advisor, helping customers with Owens Corning products.

RULES:
1. Answer ONLY from the provided product documentation.
2. For pricing, always add: "Pricing is MSRP guidance — contact your OC rep for final pricing."
3. For installation, always add: "Consult local codes and a licensed contractor."
4. If unable to answer: "I couldn't find that in our catalog. Visit owenscorning.com or call 1-800-GET-PINK."
5. Be helpful, friendly, and customer-focused."""


class RAGPipeline:
    """End-to-end RAG pipeline: retrieve → rerank → generate."""

    def __init__(self):
        self.retriever = HybridRetriever()
        self.reranker  = CrossEncoderReranker()
        self.builder   = PromptBuilder()
        self._llm      = None

    def _get_llm(self):
        if self._llm is None and settings.AZURE_OPENAI_ENDPOINT:
            try:
                from openai import AsyncAzureOpenAI
                self._llm = AsyncAzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                )
            except Exception as e:
                logger.warning(f"Could not init LLM client: {e}")
        return self._llm

    async def query(self, request: ChatQueryRequest) -> ChatQueryResponse:
        t0         = time.time()
        query_id   = str(uuid.uuid4())
        session_id = request.session_id or str(uuid.uuid4())

        is_internal = request.stream_type == StreamType.INTERNAL
        index_name  = settings.AZURE_SEARCH_INDEX_INTERNAL if is_internal else settings.AZURE_SEARCH_INDEX_EXTERNAL
        deployment  = settings.AZURE_OPENAI_DEPLOYMENT_GPT4O if is_internal else settings.AZURE_OPENAI_DEPLOYMENT_MINI
        max_tokens  = settings.INTERNAL_MAX_TOKENS if is_internal else settings.EXTERNAL_MAX_TOKENS

        # Build RBAC / scope filter
        filters = {}
        if request.domain_filter:   filters["domain"]       = request.domain_filter.value
        if request.product_filter:  filters["product_line"] = request.product_filter.value
        if request.site_filter:     filters["site"]         = request.site_filter

        # Retrieve
        candidates = await self.retriever.retrieve(
            query=request.query,
            index_name=index_name,
            top_k=settings.RAG_TOP_K_RETRIEVAL,
            filters=filters,
        )

        # Rerank
        top_chunks = await self.reranker.rerank(
            query=request.query,
            candidates=candidates,
            top_k=settings.RAG_TOP_K_RERANK,
        )

        is_gap     = not top_chunks or (top_chunks and top_chunks[0].score < settings.RAG_MIN_CONFIDENCE)
        system     = INTERNAL_SYSTEM if is_internal else EXTERNAL_SYSTEM
        messages   = self.builder.build(system, request.query, top_chunks, is_gap)
        confidence = top_chunks[0].score if top_chunks else 0.0

        # Generate
        answer = await self._generate(messages, deployment, max_tokens)

        citations = self._citations(top_chunks)
        latency   = int((time.time() - t0) * 1000)

        logger.info(f"Query [{request.stream_type.value}] latency={latency}ms gap={is_gap} conf={confidence:.2f}")

        return ChatQueryResponse(
            answer=answer,
            citations=citations,
            session_id=session_id,
            query_id=query_id,
            confidence=round(confidence, 3),
            is_knowledge_gap=is_gap,
            latency_ms=latency,
            stream_type=request.stream_type,
            timestamp=datetime.utcnow(),
        )

    async def _generate(self, messages: list, deployment: str, max_tokens: int) -> str:
        llm = self._get_llm()
        if llm is None:
            return (
                "⚠ Development mode: Azure OpenAI not configured. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in your .env file. "
                "The RAG pipeline ran successfully and retrieved context — only LLM generation is unavailable."
            )
        try:
            resp = await llm.chat.completions.create(
                model=deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Generation error: {str(e)}. Retrieved context is available but answer could not be generated."

    def _citations(self, chunks: list[RetrievedChunk]) -> list[SourceCitation]:
        seen, out = set(), []
        for c in chunks:
            key = c.metadata.get("name", c.chunk_id)
            if key not in seen:
                seen.add(key)
                out.append(SourceCitation(
                    document_name=c.metadata.get("name", "Unknown"),
                    section=c.metadata.get("section"),
                    version=c.metadata.get("version"),
                    approved_date=c.metadata.get("approved_date"),
                    confidence=round(c.score, 3),
                ))
        return out

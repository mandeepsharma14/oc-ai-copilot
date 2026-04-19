"""
Hybrid retriever — BM25 keyword + dense vector search via Azure AI Search.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    text:     str
    score:    float
    chunk_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridRetriever:

    def __init__(self):
        self._embed_client = None

    def _get_embed_client(self):
        if self._embed_client is None:
            try:
                from openai import AsyncAzureOpenAI
                from app.core.config import settings
                self._embed_client = AsyncAzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                )
            except Exception as e:
                logger.warning(f"Could not init embed client: {e}")
        return self._embed_client

    async def _embed_query(self, query: str) -> list[float]:
        from app.core.config import settings
        client = self._get_embed_client()
        if client is None:
            return []
        response = await client.embeddings.create(
            input=query[:8000],
            model=settings.AZURE_OPENAI_DEPLOYMENT_EMBED,
        )
        return response.data[0].embedding

    async def retrieve(
        self,
        query: str,
        index_name: str,
        top_k: int = 20,
        filters: Optional[dict] = None,
    ) -> list[RetrievedChunk]:
        from app.core.config import settings

        if not settings.AZURE_SEARCH_ENDPOINT:
            logger.info("Azure Search not configured — returning mock results")
            return self._mock_results(query, top_k)

        try:
            from azure.search.documents import SearchClient
            from azure.search.documents.models import VectorizedQuery
            from azure.core.credentials import AzureKeyCredential

            query_vector = await self._embed_query(query)

            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top_k,
                fields="content_vector",
            ) if query_vector else None

            # Determine select fields based on index type
            is_external = index_name == settings.AZURE_SEARCH_INDEX_EXTERNAL
            if is_external:
                select_fields = ["chunk_id", "content", "document_name",
                                 "section", "version", "approved_date",
                                 "product_line", "site"]
            else:
                select_fields = ["chunk_id", "content", "document_name",
                                 "section", "version", "approved_date",
                                 "domain", "site"]

            # Build filter — only filter on fields that exist in the index
            filter_str = self._build_filter(filters, is_external)

            client = SearchClient(
                endpoint=settings.AZURE_SEARCH_ENDPOINT,
                index_name=index_name,
                credential=AzureKeyCredential(settings.AZURE_SEARCH_ADMIN_KEY),
            )

            results = client.search(
                search_text=query,
                vector_queries=[vector_query] if vector_query else None,
                filter=filter_str,
                top=top_k,
                select=select_fields,
            )

            chunks = []
            for r in results:
                chunks.append(RetrievedChunk(
                    text=r.get("content", ""),
                    score=float(r.get("@search.score", 0.0)),
                    chunk_id=r.get("chunk_id", ""),
                    metadata={
                        "name":          r.get("document_name", ""),
                        "section":       r.get("section"),
                        "version":       r.get("version"),
                        "approved_date": r.get("approved_date"),
                        "domain":        r.get("domain"),
                        "product_line":  r.get("product_line"),
                        "site":          r.get("site"),
                    },
                ))

            client.close()

            if chunks:
                logger.info(f"Retrieved {len(chunks)} chunks from {index_name}")
                return chunks
            else:
                logger.info(f"No chunks found in {index_name}")
                return self._mock_results(query, top_k)

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return self._mock_results(query, top_k)

    def _build_filter(self, filters: Optional[dict], is_external: bool) -> Optional[str]:
        if not filters:
            return None
        clauses = []
        for k, v in filters.items():
            if not v:
                continue
            # Skip domain filter for external index (field does not exist)
            if is_external and k == "domain":
                continue
            # Skip product_line filter for internal index (field does not exist)
            if not is_external and k == "product_line":
                continue
            clauses.append(f"{k} eq '{v}'")
        return " and ".join(clauses) if clauses else None

    def _mock_results(self, query: str, top_k: int) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                text=f"Mock document content relevant to: {query}.",
                score=0.85,
                chunk_id="mock-001",
                metadata={
                    "name": "Mock Document — Development Mode",
                    "section": "§1.1",
                    "version": "Rev 1 · 2025",
                    "approved_date": "2025-01-01",
                    "domain": "engineering",
                },
            )
        ]

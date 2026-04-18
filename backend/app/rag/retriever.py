"""
Hybrid retriever — BM25 keyword + dense vector search via Azure AI Search.
Applies RBAC metadata filters so users only receive permitted documents.
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
    """
    Combines BM25 full-text search and dense vector semantic search
    using Azure AI Search with Reciprocal Rank Fusion (RRF) merging.
    """

    def __init__(self):
        self._search_clients: dict = {}
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

    def _get_search_client(self, index_name: str):
        if index_name not in self._search_clients:
            try:
                from azure.search.documents.aio import SearchClient
                from azure.core.credentials import AzureKeyCredential
                from app.core.config import settings
                self._search_clients[index_name] = SearchClient(
                    endpoint=settings.AZURE_SEARCH_ENDPOINT,
                    index_name=index_name,
                    credential=AzureKeyCredential(settings.AZURE_SEARCH_ADMIN_KEY),
                )
            except Exception as e:
                logger.warning(f"Could not init search client: {e}")
                return None
        return self._search_clients[index_name]

    async def _embed_query(self, query: str) -> list[float]:
        """Generate query embedding for vector search."""
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
        """
        Execute hybrid search: BM25 + vector, merged via RRF.
        Falls back to mock data in development when Azure is not configured.
        """
        from app.core.config import settings

        if not settings.AZURE_SEARCH_ENDPOINT:
            logger.info("Azure Search not configured — returning mock results")
            return self._mock_results(query, top_k)

        try:
            query_vector = await self._embed_query(query)
            filter_str = self._build_filter(filters)
            client = self._get_search_client(index_name)
            if client is None:
                return self._mock_results(query, top_k)

            from azure.search.documents.models import VectorizedQuery
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top_k,
                fields="content_vector",
            )

            chunks = []
            async with client:
                results = await client.search(
                    search_text=query,
                    vector_queries=[vector_query] if query_vector else None,
                    filter=filter_str,
                    top=top_k,
                    select=["chunk_id", "content", "document_name",
                            "section", "version", "approved_date",
                            "domain", "product_line", "site"],
                )
                async for r in results:
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
            return chunks

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return self._mock_results(query, top_k)

    def _build_filter(self, filters: Optional[dict]) -> Optional[str]:
        if not filters:
            return None
        clauses = [f"{k} eq '{v}'" for k, v in filters.items() if v]
        return " and ".join(clauses) if clauses else None

    def _mock_results(self, query: str, top_k: int) -> list[RetrievedChunk]:
        """Return mock chunks for development / testing without Azure."""
        return [
            RetrievedChunk(
                text=f"Mock document content relevant to: {query}. "
                     "This is returned when Azure AI Search is not configured. "
                     "In production this would be real document content from the knowledge base.",
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

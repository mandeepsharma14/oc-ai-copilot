"""
Cross-encoder reranker — scores query-chunk pairs for relevance.
Uses ms-marco-MiniLM-L-12-v2 locally or falls back to score-based sorting.
"""
from __future__ import annotations
import logging
from app.rag.retriever import RetrievedChunk

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """
    Reranks retrieved chunks using a cross-encoder model.
    Falls back to retrieval score ordering if model unavailable.
    """

    def __init__(self):
        self._model = None
        self._model_loaded = False

    def _load_model(self):
        if self._model_loaded:
            return
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
            self._model_loaded = True
            logger.info("Cross-encoder reranker loaded")
        except Exception as e:
            logger.warning(f"Cross-encoder unavailable (using score sort): {e}")
            self._model_loaded = True

    async def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int = 6,
        min_score: float = 0.0,
    ) -> list[RetrievedChunk]:
        """
        Rerank candidates using cross-encoder.
        Returns top_k most relevant chunks above min_score threshold.
        """
        if not candidates:
            return []

        self._load_model()

        if self._model is not None:
            try:
                pairs = [(query, c.text[:512]) for c in candidates]
                scores = self._model.predict(pairs)
                ranked = sorted(
                    zip(candidates, scores),
                    key=lambda x: float(x[1]),
                    reverse=True,
                )
                result = [c for c, s in ranked[:top_k] if float(s) > min_score]
                # Update scores with reranker scores
                for chunk, score in ranked[:top_k]:
                    chunk.score = round(float(score), 4)
                return result or candidates[:top_k]
            except Exception as e:
                logger.error(f"Reranking failed: {e}")

        # Fallback: sort by retrieval score
        return sorted(candidates, key=lambda c: c.score, reverse=True)[:top_k]

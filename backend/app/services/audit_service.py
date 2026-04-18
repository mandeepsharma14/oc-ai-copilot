"""Audit service — immutable logging of every query and AI response."""
from __future__ import annotations
import json
import logging
from datetime import datetime
from app.models.schemas import ChatQueryResponse, StreamType

logger = logging.getLogger(__name__)


class AuditService:
    """
    Logs every query interaction to Azure SQL (production) or local log (dev).
    Audit records are immutable — no update or delete permitted.
    """

    async def log_query(
        self,
        user_id:     str,
        query:       str,
        response:    ChatQueryResponse,
        stream_type: StreamType,
    ) -> None:
        record = {
            "query_id":        response.query_id,
            "session_id":      response.session_id,
            "user_id":         user_id,
            "stream_type":     stream_type.value,
            "query_text":      query,
            "answer_text":     response.answer[:4000],
            "citations":       [c.model_dump() for c in response.citations],
            "confidence":      response.confidence,
            "is_knowledge_gap":response.is_knowledge_gap,
            "latency_ms":      response.latency_ms,
            "timestamp":       response.timestamp.isoformat(),
        }
        try:
            await self._write(record)
        except Exception as e:
            logger.error(f"Audit log write failed: {e}")

    async def _write(self, record: dict) -> None:
        from app.core.config import settings
        if settings.ENVIRONMENT == "production":
            await self._write_sql(record)
        else:
            logger.info(f"AUDIT | {json.dumps(record, default=str)[:200]}...")

    async def _write_sql(self, record: dict) -> None:
        """Write to Azure SQL immutable audit table in production."""
        try:
            import aioodbc
            from app.core.config import settings
            conn_str = settings.AZURE_SQL_CONNECTION_STRING
            async with await aioodbc.connect(dsn=conn_str) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO query_audit_log
                            (query_id, session_id, user_id, stream_type,
                             query_text, answer_text, citations_json,
                             confidence, is_knowledge_gap, latency_ms, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        record["query_id"], record["session_id"],
                        record["user_id"], record["stream_type"],
                        record["query_text"], record["answer_text"],
                        json.dumps(record["citations"]),
                        record["confidence"], record["is_knowledge_gap"],
                        record["latency_ms"], datetime.utcnow(),
                    )
                    await conn.commit()
        except Exception as e:
            logger.error(f"SQL audit write failed: {e}")

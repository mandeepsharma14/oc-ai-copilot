"""Chat query endpoints — internal and external streams."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ChatQueryRequest, ChatQueryResponse
from app.services.chat_service import process_query
from app.services.audit_service import AuditService
from app.core.security import get_current_user

router  = APIRouter()
logger  = logging.getLogger(__name__)
_audit  = AuditService()


@router.post(
    "/query",
    response_model=ChatQueryResponse,
    summary="Submit a knowledge query",
    description=(
        "Query the OC knowledge base. "
        "Use stream_type='internal' for employee queries, 'external' for customer queries."
    ),
)
async def query(
    request:      ChatQueryRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatQueryResponse:
    try:
        response = await process_query(request)

        # Fire-and-forget audit log
        try:
            await _audit.log_query(
                user_id=current_user.get("user_id", "anonymous"),
                query=request.query,
                response=response,
                stream_type=request.stream_type,
            )
        except Exception as audit_err:
            logger.warning(f"Audit log failed (non-fatal): {audit_err}")

        return response

    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}",
        )


@router.get(
    "/history/{session_id}",
    summary="Get conversation history",
)
async def get_history(
    session_id:   str,
    current_user: dict = Depends(get_current_user),
):
    # TODO: fetch from Cosmos DB
    return {"session_id": session_id, "messages": [], "status": "ok"}

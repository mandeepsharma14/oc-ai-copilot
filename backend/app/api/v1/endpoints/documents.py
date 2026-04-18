"""Document ingestion and listing endpoints."""
import logging
import tempfile
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.models.schemas import (
    DocumentIngestRequest, DocumentIngestResponse,
    DocumentRecord, StreamType,
)
from app.services.document_service import ingest_document, list_documents
from app.core.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".txt", ".md"}
MAX_FILE_SIZE_MB   = 50


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    summary="Trigger document ingestion",
)
async def ingest(
    request:      DocumentIngestRequest,
    current_user: dict = Depends(get_current_user),
) -> DocumentIngestResponse:
    try:
        return await ingest_document(request)
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/upload",
    response_model=DocumentIngestResponse,
    summary="Upload and ingest a document file",
)
async def upload(
    file:        UploadFile = File(...),
    stream_type: str        = Form(...),
    domain:      str        = Form(None),
    product_line:str        = Form(None),
    site:        str        = Form(None),
    current_user:dict       = Depends(get_current_user),
) -> DocumentIngestResponse:
    # Validate file type
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' not supported. Allowed: {ALLOWED_EXTENSIONS}",
        )

    # Write to temp file and ingest
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit")
        tmp.write(content)
        tmp_path = tmp.name

    try:
        request = DocumentIngestRequest(
            source_type=  "upload",
            stream_type=  StreamType(stream_type),
            domain=       domain,
            product_line= product_line,
            site=         site,
            metadata=     {"name": file.filename},
        )
        return await ingest_document(request, file_path=tmp_path)
    finally:
        os.unlink(tmp_path)


@router.get(
    "/",
    response_model=list[DocumentRecord],
    summary="List documents in knowledge base",
)
async def get_documents(
    stream_type:  str       = "internal",
    domain:       str       = None,
    current_user: dict      = Depends(get_current_user),
) -> list[DocumentRecord]:
    return await list_documents(stream_type, domain)

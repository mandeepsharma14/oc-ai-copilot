"""Health check endpoint."""
from datetime import datetime
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow(),
    )

"""OC AI Copilot — FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import chat, documents, admin, health
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"OC AI Copilot starting — environment: {settings.ENVIRONMENT}")
    yield
    print("OC AI Copilot shutting down")


app = FastAPI(
    title="OC AI Copilot API",
    description="Enterprise Knowledge Assistant — Internal + External streams",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,     prefix="/api/v1",           tags=["health"])
app.include_router(chat.router,       prefix="/api/v1/chat",       tags=["chat"])
app.include_router(documents.router,  prefix="/api/v1/documents",  tags=["documents"])
app.include_router(admin.router,      prefix="/api/v1/admin",      tags=["admin"])

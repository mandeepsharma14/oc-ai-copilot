"""Application configuration — loaded from environment variables."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production-min-32-chars"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-05-01-preview"
    AZURE_OPENAI_DEPLOYMENT_GPT4O: str = "gpt-4o"
    AZURE_OPENAI_DEPLOYMENT_MINI: str = "gpt-4o-mini"
    AZURE_OPENAI_DEPLOYMENT_EMBED: str = "text-embedding-3-large"

    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: str = ""
    AZURE_SEARCH_ADMIN_KEY: str = ""
    AZURE_SEARCH_INDEX_INTERNAL: str = "oc-internal-docs"
    AZURE_SEARCH_INDEX_EXTERNAL: str = "oc-external-docs"

    # Azure Entra ID
    AZURE_TENANT_ID: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 3600

    # Cosmos DB
    COSMOS_ENDPOINT: str = ""
    COSMOS_KEY: str = ""
    COSMOS_DATABASE: str = "oc-copilot"

    # RAG
    RAG_TOP_K_RETRIEVAL: int = 20
    RAG_TOP_K_RERANK: int = 6
    RAG_CHUNK_SIZE: int = 512
    RAG_CHUNK_OVERLAP: int = 102
    RAG_MIN_CONFIDENCE: float = 0.35
    INTERNAL_MAX_TOKENS: int = 2048
    EXTERNAL_MAX_TOKENS: int = 1024

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

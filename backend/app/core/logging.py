"""Structured logging configuration."""
import logging
import sys
from app.core.config import settings


def configure_logging():
    """Configure structured JSON logging for production, pretty for dev."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.ENVIRONMENT == "production":
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","service":"oc-copilot","message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Suppress noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

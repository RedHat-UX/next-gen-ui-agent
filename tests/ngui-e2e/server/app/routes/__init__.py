"""API route handlers."""

from .generate import router as generate_router
from .health import router as health_router

__all__ = ["health_router", "generate_router"]

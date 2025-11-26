"""API route handlers."""
from .generate import router as generate_router
from .health import router as health_router
from .prometheus import router as prometheus_router

__all__ = ["health_router", "prometheus_router", "generate_router"]


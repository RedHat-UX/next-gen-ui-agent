"""FastAPI application for the NGUI E2E server."""

from contextlib import asynccontextmanager

from app.llm import test_llm_connection
from app.routes import generate_router, health_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup checks (e.g. LLM reachability) then yield."""
    print("Checking LLM reachability...")
    ok = await test_llm_connection()
    if not ok:
        print(
            "WARNING: LLM check failed. /generate requests may return 503 until the LLM is reachable."
        )
    yield
    # shutdown: nothing to do


# Create FastAPI app
app = FastAPI(
    title="NGUI E2E API",
    description="Next Gen UI Agent API for AI-powered UI component generation",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(generate_router)

"""FastAPI application for the NGUI E2E server."""

from app.routes import generate_router, health_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="NGUI E2E API",
    description="Next Gen UI Agent API for AI-powered UI component generation",
    version="1.0.0",
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

"""FastAPI application for the NGUI E2E server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate_router, health_router

# Create FastAPI app
app = FastAPI()

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

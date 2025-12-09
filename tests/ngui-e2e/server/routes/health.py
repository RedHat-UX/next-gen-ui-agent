"""Health check and model info endpoints."""

from config import BASE_URL, MODEL
from fastapi import APIRouter
from llm import llm

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint to verify server and Ollama connectivity."""
    try:
        # Test Ollama connection
        _ = llm.invoke("test")
        return {
            "status": "healthy",
            "ollama_connected": True,
            "model": MODEL,
            "base_url": BASE_URL,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_connected": False,
            "error": str(e),
            "model": MODEL,
            "base_url": BASE_URL,
        }


@router.get("/model-info")
async def get_model_info():
    """Get information about the connected LLM model."""
    return {
        "name": MODEL,
        "baseUrl": BASE_URL,
    }

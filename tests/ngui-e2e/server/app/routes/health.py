"""Health check and model info endpoints."""

from app.config import get_llm_display_info
from app.llm import complete_for_filtering
from app.models import ErrorCode
from app.utils.response import create_error_response
from fastapi import APIRouter, status

router = APIRouter()


@router.get("/model-info")
async def model_info():
    """Return model name and base URL for the E2E client Model Info tab."""
    info = get_llm_display_info()
    return {"name": info["model_id"], "baseUrl": info["base_url"]}


@router.get("/api/v1/health")
async def health_check():
    """Health check endpoint to verify server connectivity."""
    info = get_llm_display_info()
    return {
        "status": "ok",
        "mode": info["mode"],
        "model": info["model_id"],
        "base_url": info["base_url"],
    }


@router.get("/api/v1/wdyk")
async def wdyk():
    """Test LLM connectivity (uses configured backend: local or LlamaStack)."""
    try:
        question = "What do you know? Keep it VERY short."
        response_text = await complete_for_filtering(question)
        return {"question": question, "response": response_text}
    except Exception as e:
        return create_error_response(
            error_code=ErrorCode.LLM_CONNECTION_ERROR,
            message="Failed to connect to LLM",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=str(e),
            suggestion="Check LLM connection (Ollama/Gemini or LlamaStack) and configuration",
        )

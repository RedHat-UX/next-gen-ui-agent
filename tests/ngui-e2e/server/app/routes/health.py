"""Health check and model info endpoints."""

from app.config import LLAMA_STACK_BASE_URL, NGUI_MODEL
from app.llm import get_llm_client
from app.models import ErrorCode
from app.utils.response import create_error_response
from fastapi import APIRouter, status
from llama_stack_client.types import UserMessage

router = APIRouter()


@router.get("/api/v1/health")
async def health_check():
    """Health check endpoint to verify server connectivity."""
    return {
        "status": "ok",
        "model": NGUI_MODEL,
        "base_url": LLAMA_STACK_BASE_URL,
    }


@router.get("/api/v1/wdyk")
async def wdyk():
    """Test LLM connectivity endpoint."""
    try:
        question = "What do you know? Keep it VERY short."
        client = get_llm_client()
        user_message = UserMessage(role="user", content=question)
        response = await client.inference.chat_completion(
            model_id=NGUI_MODEL,
            messages=[user_message],
        )
        return {
            "question": question,
            "response": response.completion_message.content,
        }
    except Exception as e:
        return create_error_response(
            error_code=ErrorCode.LLM_CONNECTION_ERROR,
            message="Failed to connect to LLM",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=str(e),
            suggestion="Check if LlamaStack is running and configured correctly",
        )

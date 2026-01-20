"""LlamaStack client setup and connection testing."""

import ssl

from app.config import LLAMA_STACK_BASE_URL, LLAMA_STACK_TLS_CA_CERT_PATH, NGUI_MODEL
from llama_stack_client import AsyncLlamaStackClient, DefaultAsyncHttpxClient
from llama_stack_client.types import UserMessage


def get_llamastack_client():
    """Create and return a configured LlamaStack client."""
    ctx = ssl.create_default_context(
        cafile=LLAMA_STACK_TLS_CA_CERT_PATH,
    )
    return AsyncLlamaStackClient(
        base_url=LLAMA_STACK_BASE_URL,
        http_client=DefaultAsyncHttpxClient(verify=ctx),
    )


async def test_llm_connection():
    """Test the LlamaStack connection and print diagnostics."""
    print("Testing LlamaStack connection...")
    try:
        client = get_llamastack_client()
        user_message = UserMessage(role="user", content="test")
        response = await client.inference.chat_completion(
            model_id=NGUI_MODEL,
            messages=[user_message],
        )
        print(f"✓ LlamaStack connection successful! Response type: {type(response)}")
        return True
    except Exception as e:
        print("✗ LlamaStack connection FAILED!")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")
        print(f"  Full error: {repr(e)}")

        # Try to get more details from the exception
        import traceback

        print("\nFull traceback:")
        traceback.print_exc()

        # Check for underlying cause
        if hasattr(e, "__cause__") and e.__cause__:
            print(f"\nUnderlying cause: {type(e.__cause__).__name__}: {e.__cause__}")

        print("\nThis may cause failures when processing requests.\n")
        return False


# Singleton client instance
_client_instance = None


def get_llm_client():
    """Get or create the singleton LlamaStack client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = get_llamastack_client()
    return _client_instance

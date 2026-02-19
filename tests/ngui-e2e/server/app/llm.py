"""LLM client setup: LlamaStack (deployed) or local/direct (Ollama, Gemini, etc.)."""

import ssl

from app.config import (
    LLAMA_STACK_BASE_URL,
    LLAMA_STACK_TLS_CA_CERT_PATH,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    NGUI_MODEL,
    USE_LOCAL_LLM,
)

# -----------------------------------------------------------------------------
# Local / direct LLM (Ollama, Gemini via OpenAI-compatible API)
# -----------------------------------------------------------------------------
_local_llm = None


def get_local_llm():
    """Get or create the LangChain ChatOpenAI instance for local mode."""
    global _local_llm
    if _local_llm is not None:
        return _local_llm
    if not USE_LOCAL_LLM:
        return None

    import httpx
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr

    api_key = LLM_API_KEY or "ollama"
    _local_llm = ChatOpenAI(
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        api_key=SecretStr(api_key),
        http_client=httpx.Client(verify=False, timeout=60.0),
        http_async_client=httpx.AsyncClient(verify=False, timeout=60.0),
    )
    return _local_llm


async def complete_for_filtering_local(prompt: str) -> str:
    """Call the local LLM for data-filtering prompts. Used when USE_LOCAL_LLM is True."""
    llm = get_local_llm()
    if llm is None:
        raise RuntimeError("Local LLM not configured (USE_LOCAL_LLM is False)")
    msg = await llm.ainvoke(prompt)
    return msg.content if msg and hasattr(msg, "content") else str(msg)


# -----------------------------------------------------------------------------
# LlamaStack client (deployed / Lightrail)
# -----------------------------------------------------------------------------


def get_llamastack_client():
    """Create and return a configured LlamaStack client."""
    ctx = ssl.create_default_context(
        cafile=LLAMA_STACK_TLS_CA_CERT_PATH,
    )
    from llama_stack_client import AsyncLlamaStackClient, DefaultAsyncHttpxClient

    return AsyncLlamaStackClient(
        base_url=LLAMA_STACK_BASE_URL,
        http_client=DefaultAsyncHttpxClient(verify=ctx),
    )


async def complete_for_filtering_llamastack(prompt: str) -> str:
    """Call LlamaStack for data-filtering prompts. Used when USE_LOCAL_LLM is False."""
    from llama_stack_client.types import UserMessage

    client = get_llm_client()
    user_message = UserMessage(role="user", content=prompt)
    response = await client.inference.chat_completion(
        model_id=NGUI_MODEL,
        messages=[user_message],
    )
    return response.completion_message.content


async def complete_for_filtering(prompt: str) -> str:
    """Call the configured LLM (local or LlamaStack) for filtering. Use this in data_sources."""
    if USE_LOCAL_LLM:
        return await complete_for_filtering_local(prompt)
    return await complete_for_filtering_llamastack(prompt)


async def test_llm_connection():
    """Test the LLM connection and print diagnostics (same path for local and LlamaStack)."""
    from app.config import get_llm_display_info

    info = get_llm_display_info()
    label = "Local LLM" if info["mode"] == "local" else "LlamaStack"
    print(f"Testing {label} connection...")
    try:
        _ = await complete_for_filtering("test")
        print(f"✓ {label} connection successful!")
        return True
    except Exception as e:
        _log_connection_error(label, e)
        return False


def _log_connection_error(label: str, e: Exception) -> None:
    print(f"✗ {label} connection FAILED!")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    import traceback

    traceback.print_exc()
    if hasattr(e, "__cause__") and e.__cause__:
        print(f"\nUnderlying cause: {type(e.__cause__).__name__}: {e.__cause__}")
    # HTTP response details when present (e.g. 403, 401)
    if hasattr(e, "response") and e.response is not None:
        r = e.response
        print("\nHTTP Response details:")
        print(f"  Status: {getattr(r, 'status_code', 'N/A')}")
        print(f"  Headers: {getattr(r, 'headers', 'N/A')}")
        body = getattr(r, "text", None) or getattr(r, "content", b"")
        if body:
            text = body[:1000] if isinstance(body, bytes) else body[:1000]
            print(f"  Body: {text}")
    print("\nThis may cause failures when processing requests.\n")


# Singleton LlamaStack client instance
_client_instance = None


def get_llm_client():
    """Get or create the singleton LlamaStack client. Only valid when USE_LOCAL_LLM is False."""
    global _client_instance
    if _client_instance is None:
        _client_instance = get_llamastack_client()
    return _client_instance

"""LLM client setup and connection testing."""

import httpx
import urllib3
from config import API_KEY, BASE_URL, MODEL
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# Suppress SSL warnings for internal corporate APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create BOTH sync and async httpx clients with SSL verification disabled
# (LangChain uses sync for invoke() and async for ainvoke())
sync_client = httpx.Client(verify=False, timeout=60.0)
async_client = httpx.AsyncClient(verify=False, timeout=60.0)

# For Ollama and similar local LLMs, a dummy API key is acceptable
api_key = API_KEY or "ollama"

llm = ChatOpenAI(
    model=MODEL,
    base_url=BASE_URL,
    api_key=SecretStr(api_key),
    http_client=sync_client,
    http_async_client=async_client,
)


def test_llm_connection():
    """Test the LLM connection and print diagnostics."""
    print("Testing LLM connection...")
    try:
        test_response = llm.invoke("test")
        print(f"✓ LLM connection successful! Response type: {type(test_response)}")
    except Exception as e:
        print("✗ LLM connection FAILED!")
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

        # Check for response attribute
        if hasattr(e, "response"):
            print("\nHTTP Response details:")
            print(f"  Status: {getattr(e.response, 'status_code', 'N/A')}")
            print(f"  Headers: {getattr(e.response, 'headers', 'N/A')}")
            print(f"  Body: {getattr(e.response, 'text', 'N/A')[:1000]}")

        print("\nThis may cause failures when processing requests.\n")


# Test the connection on module load
test_llm_connection()

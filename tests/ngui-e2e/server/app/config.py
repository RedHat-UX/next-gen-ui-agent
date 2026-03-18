"""Configuration and logging setup for the NGUI E2E server."""

import logging
import os

from dotenv import load_dotenv
from next_gen_ui_agent.agent_config import AgentConfig

# Load environment variables from .env (e.g. when running locally)
load_dotenv()

# Configure logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Set next_gen_ui_agent logger to INFO level
logging.getLogger("next_gen_ui_agent").setLevel(logging.INFO)

# -----------------------------------------------------------------------------
# Local / direct LLM (Ollama, Gemini via OpenAI-compatible API)
# When set, the server uses LangGraph + ChatOpenAI instead of LlamaStack.
# -----------------------------------------------------------------------------
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.2:3b")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY") or ""

# LlamaStack Configuration
# Use LLAMA_STACK_BASE_URL as default, with LIGHTRAIL_LLAMA_STACK_BASE_URL as fallback
# This makes it work for both Lightrail deployments and other environments
LLAMA_STACK_BASE_URL = os.environ.get("LLAMA_STACK_BASE_URL") or os.environ.get(
    "LIGHTRAIL_LLAMA_STACK_BASE_URL"
)
LLAMA_STACK_TLS_CA_CERT_PATH = os.environ.get(
    "LLAMA_STACK_TLS_CA_CERT_PATH"
) or os.environ.get("LIGHTRAIL_LLAMA_STACK_TLS_SERVICE_CA_CERT_PATH")

# Use NGUI_MODEL to match naming convention in MCP and A2A servers
NGUI_MODEL = os.environ.get("NGUI_MODEL")

# Mode: use local/direct LLM when LLM_BASE_URL is set and LlamaStack is not configured
USE_LOCAL_LLM = bool(LLM_BASE_URL and not LLAMA_STACK_BASE_URL)


def get_llm_display_info() -> dict:
    """Single source for model id, base URL, and mode (used by health, model-info, generate metadata)."""
    if USE_LOCAL_LLM:
        return {
            "model_id": LLM_MODEL or "unknown",
            "base_url": LLM_BASE_URL or "",
            "mode": "local",
        }
    return {
        "model_id": NGUI_MODEL or "unknown",
        "base_url": LLAMA_STACK_BASE_URL or "",
        "mode": "llamastack",
    }


if USE_LOCAL_LLM:
    # Validate required env for local mode
    if not LLM_MODEL:
        raise ValueError(
            "LLM_MODEL must be set when using local LLM (LLM_BASE_URL set)"
        )

# Debug logging
print("\n" + "=" * 60)
print("LLM CONFIGURATION DEBUG")
print("=" * 60)
if USE_LOCAL_LLM:
    print("Mode: LOCAL (direct LLM - Ollama, Gemini, etc.)")
    print(f"Model: {LLM_MODEL}")
    print(f"Base URL: {LLM_BASE_URL}")
    print(f"API Key: {'SET' if LLM_API_KEY else 'NOT SET'}")
else:
    print("Mode: LLAMASTACK")
    print(f"Model ID: {NGUI_MODEL}")
    print(f"Base URL: {LLAMA_STACK_BASE_URL}")
    print(f"TLS Cert Path: {LLAMA_STACK_TLS_CA_CERT_PATH}")
print("=" * 60 + "\n")

# Data configuration
MAX_DATA_SIZE_MB = 10

# Default data file path
DEFAULT_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "movies_data.json")

# Available movies list for suggestions
AVAILABLE_MOVIES = [
    "Toy Story",
    "The Shawshank Redemption",
    "The Dark Knight",
    "Inception",
    "The Matrix",
    "Interstellar",
]

# NGUI agent configuration
# All components are available by default in next_gen_ui_agent
NGUI_CONFIG = AgentConfig()

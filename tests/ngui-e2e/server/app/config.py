"""Configuration and logging setup for the NGUI E2E server."""

import logging
import os

from next_gen_ui_agent.agent_config import AgentConfig

# Configure logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Set next_gen_ui_agent logger to INFO level
logging.getLogger("next_gen_ui_agent").setLevel(logging.INFO)

# Lightrail/LlamaStack Configuration
# These environment variables are injected by Lightrail Local or production environment
LIGHTRAIL_LLAMA_STACK_BASE_URL = os.environ.get("LIGHTRAIL_LLAMA_STACK_BASE_URL")
LIGHTRAIL_LLAMA_STACK_TLS_SERVICE_CA_CERT_PATH = os.environ.get(
    "LIGHTRAIL_LLAMA_STACK_TLS_SERVICE_CA_CERT_PATH"
)
MYAPP_MODEL_ID = os.environ.get("MYAPP_MODEL_ID")

# Debug logging for LlamaStack configuration
print("\n" + "=" * 60)
print("LLAMASTACK CONFIGURATION DEBUG")
print("=" * 60)
print(f"Model ID: {MYAPP_MODEL_ID}")
print(f"Base URL: {LIGHTRAIL_LLAMA_STACK_BASE_URL}")
print(f"TLS Cert Path: {LIGHTRAIL_LLAMA_STACK_TLS_SERVICE_CA_CERT_PATH}")
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
# Compatible with next_gen_ui_agent 0.3.x
NGUI_CONFIG = AgentConfig(unsupported_components=True)

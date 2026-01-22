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

# Debug logging for LlamaStack configuration
print("\n" + "=" * 60)
print("LLAMASTACK CONFIGURATION DEBUG")
print("=" * 60)
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

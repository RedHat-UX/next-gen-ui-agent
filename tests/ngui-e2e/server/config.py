"""Configuration and logging setup for the NGUI E2E server."""

import logging
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to show INFO level messages from next_gen_ui_agent
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Set next_gen_ui_agent logger to INFO level
logging.getLogger("next_gen_ui_agent").setLevel(logging.INFO)

# Validate required environment variables
required_env_vars = ["LLM_MODEL", "LLM_BASE_URL"]
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")

# Configuration loaded from environment variables
MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("LLM_API_KEY")

# Debug logging for LLM configuration
print("\n" + "=" * 60)
print("LLM CONFIGURATION DEBUG")
print("=" * 60)
print(f"Model: {MODEL}")
print(f"Base URL: {BASE_URL}")
print(f"API Key: {'SET (length=' + str(len(API_KEY)) + ')' if API_KEY else 'NOT SET'}")
print("=" * 60 + "\n")

# Agent configuration constants
MOVIES_AGENT_RECURSION_LIMIT = 10

# NGUI agent configuration
NGUI_CONFIG = {
    "configurable": {
        "component_system": "json",
        "unsupported_components": True,  # Enable experimental components like chart, table, set-of-cards
    }
}

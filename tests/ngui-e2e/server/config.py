"""Configuration and logging setup for the NGUI E2E server."""

import logging
import os

from dotenv import load_dotenv
from next_gen_ui_agent.types import AgentConfigDataType

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

_COMMON_OVERRIDES = {
    "created": "date",  # Data key "created" -> formatter "date"
}

# Shared data types configuration used by both agent configs and LangGraph configurable
SHARED_DATA_TYPES = {
    "products": AgentConfigDataType(
        formatter_overrides={
            **_COMMON_OVERRIDES,
        },
        on_row_click="onRowClick",
    ),
    "get_openshift_pods": AgentConfigDataType(
        formatter_overrides={
            **_COMMON_OVERRIDES,
        },
        on_row_click="onRowClick",
    ),
    "get_openshift_nodes": AgentConfigDataType(
        formatter_overrides={
            **_COMMON_OVERRIDES,
            "status": "node_status",
            "cpu": "cpu_usage",
            "memory": "memory_usage",
            "version": "version_label",
        },
        on_row_click="onRowClick",
    ),
    "pod_data": AgentConfigDataType(
        formatter_overrides={
            **_COMMON_OVERRIDES,
        },
    ),
    "cluster_info": AgentConfigDataType(
        formatter_overrides={
            **_COMMON_OVERRIDES,
            "last_backup": "date",
            "cpu_usage_percent": "cpu_usage",
            "memory_usage_percent": "memory_usage",
            "*url*": "url",  # Pattern match: any key containing "url" -> "url" formatter
        },
    ),
}


# Convert Pydantic models to dict format for LangGraph configurable
def _convert_data_types_to_dict(data_types):
    """Convert AgentConfigDataType Pydantic models to dict format."""
    return {
        key: {"formatter_overrides": value.formatter_overrides}
        for key, value in data_types.items()
    }


NGUI_CONFIG = {
    "configurable": {
        "component_system": "json",
        "data_types": _convert_data_types_to_dict(SHARED_DATA_TYPES),
    }
}

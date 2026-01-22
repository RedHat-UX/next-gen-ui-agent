"""Data sources for the e2e server."""

from data_sources.data_loader import get_namespaces_data, get_nodes_data, get_pods_data
from data_sources.inline import process_inline_data
from data_sources.mock_mcp_server import MockOpenShiftMCPServer
from data_sources.movies import invoke_movies_agent

__all__ = [
    "MockOpenShiftMCPServer",
    "get_namespaces_data",
    "get_nodes_data",
    "get_pods_data",
    "invoke_movies_agent",
    "process_inline_data",
]

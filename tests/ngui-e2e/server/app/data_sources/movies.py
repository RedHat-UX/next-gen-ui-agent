"""Movies data source module for LlamaStack.

This module provides a reference implementation for how a movies agent
could work with LlamaStack. Unlike the LangGraph version, this doesn't use
agent tools but rather provides utility functions for working with movie data.

Note: This is adapted from the LangGraph version to work with LlamaStack.
The actual data fetching is handled by the filtering module or default data.
"""

from typing import Any, Optional

from app.utils.logging import log_info, log_section


def get_movie_data_summary(data: Any) -> dict[str, Any]:
    """
    Get a summary of movie data for logging and debugging.

    Args:
        data: Movie data (list or dict)

    Returns:
        Dictionary with summary information
    """
    summary = {
        "type": type(data).__name__,
        "is_list": isinstance(data, list),
        "count": 0,
        "has_data": False,
    }

    if isinstance(data, list):
        summary["count"] = len(data)
        summary["has_data"] = len(data) > 0

        if len(data) > 0:
            # Analyze first item to get field info
            first_item = data[0]
            if isinstance(first_item, dict):
                summary["fields"] = list(first_item.keys())
                summary["sample_keys"] = list(first_item.keys())[:5]
    elif isinstance(data, dict):
        summary["count"] = 1
        summary["has_data"] = True
        summary["fields"] = list(data.keys())
        summary["sample_keys"] = list(data.keys())[:5]

    return summary


def log_movie_data_info(data: Any, source: str = "unknown") -> None:
    """
    Log information about movie data for debugging.

    Args:
        data: Movie data to log
        source: Source of the data (e.g., "inline", "default", "filtered")
    """
    log_section(f"MOVIE DATA INFO - Source: {source}")

    summary = get_movie_data_summary(data)

    log_info(f"Data type: {summary['type']}")
    log_info(f"Is list: {summary['is_list']}")
    log_info(f"Count: {summary['count']}")
    log_info(f"Has data: {summary['has_data']}")

    if "fields" in summary:
        log_info(f"Fields: {', '.join(summary['sample_keys'])}")
        if len(summary["fields"]) > 5:
            log_info(f"  (... and {len(summary['fields']) - 5} more fields)")


def validate_movie_data(data: Any) -> tuple[bool, Optional[str]]:
    """
    Validate movie data structure.

    Args:
        data: Data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if data is None:
        return False, "Data is None"

    if not data:
        return False, "Data is empty"

    if isinstance(data, list):
        if len(data) == 0:
            return False, "Data list is empty"

        # Check first item has some structure
        first_item = data[0]
        if not isinstance(first_item, dict):
            return (
                False,
                f"Expected list of dicts, got list of {type(first_item).__name__}",
            )

        if len(first_item) == 0:
            return False, "First item in list has no fields"

    elif isinstance(data, dict):
        if len(data) == 0:
            return False, "Data dict is empty"

    else:
        return False, f"Expected list or dict, got {type(data).__name__}"

    return True, None


def extract_movie_fields(data: Any) -> list[str]:
    """
    Extract field names from movie data.

    Args:
        data: Movie data (list of dicts or single dict)

    Returns:
        List of field names
    """
    if isinstance(data, list) and len(data) > 0:
        first_item = data[0]
        if isinstance(first_item, dict):
            return list(first_item.keys())
    elif isinstance(data, dict):
        return list(data.keys())

    return []


# Reference: How the LangGraph version worked
# ==========================================
#
# The LangGraph version used:
# 1. create_react_agent with tools (search_movie, get_all_movies)
# 2. Movies agent invocation with recursion limit
# 3. LangChain message serialization
# 4. Tool call extraction from agent response
#
# In LlamaStack, we use:
# 1. Direct data processing (inline or default)
# 2. Intelligent filtering with LLM
# 3. ToolExecutionStep for data passing
# 4. Event-based agent interaction
#
# This module provides utilities that bridge the conceptual gap
# between the two approaches, making it easier to work with
# movie data in the LlamaStack environment.

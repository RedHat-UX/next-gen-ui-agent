"""Utilities for creating API responses."""

from typing import Any, Optional


def create_error_response(
    error: str,
    details: str,
    raw_response: Optional[Any] = None,
    suggestion: Optional[str] = None,
    agent_messages: Optional[list] = None,
) -> dict[str, Any]:
    """Helper function to create standardized error responses."""
    response: dict[str, Any] = {
        "error": error,
        "details": details,
    }

    if raw_response is not None:
        response["raw_response"] = str(raw_response)

    if suggestion:
        response["suggestion"] = suggestion

    # Add agent messages to metadata for debugging
    if agent_messages:
        response["metadata"] = {"agentMessages": agent_messages}

    return response

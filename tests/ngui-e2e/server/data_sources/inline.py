"""Inline data processing for generate endpoint.

This module handles inline data for non-OpenShift queries (e.g., products, users).
OpenShift queries use the mock MCP server instead.
"""

import json
from typing import Any, Optional

from utils.inline_data import build_inline_messages
from utils.logging import log_info
from utils.response import create_error_response


def process_inline_data(
    prompt: str, data: Any, data_type: Optional[str] = None
) -> tuple[Optional[dict], Optional[list[dict]], Optional[dict], Optional[dict]]:
    """
    Process inline data provided in the request.

    Args:
        prompt: User prompt
        data: Inline data payload
        data_type: Optional data type identifier

    Returns:
        Tuple of (movie_response, agent_messages, inline_data_context, error_response)
        If successful, error_response is None.
        If failed, movie_response, agent_messages and inline_data_context are None.
    """
    log_info("Step 1: Using inline data provided in request.")

    inline_payload = data

    # Handle string payload
    if isinstance(inline_payload, str):
        inline_payload = inline_payload.strip()
        if not inline_payload:
            return (
                None,
                None,
                create_error_response(
                    "Invalid data",
                    "Inline data string cannot be empty",
                    suggestion="Provide valid JSON data or omit the field.",
                ),
            )
        try:
            inline_payload = json.loads(inline_payload)
        except json.JSONDecodeError as e:
            return (
                None,
                None,
                create_error_response(
                    "Invalid data",
                    f"Inline data must be valid JSON. Parse error: {str(e)}",
                    suggestion="Provide JSON (object/array/string) that can be parsed.",
                ),
            )

    # Serialize to JSON
    try:
        inline_data_json = json.dumps(inline_payload)
    except (TypeError, ValueError) as e:
        return (
            None,
            None,
            None,
            create_error_response(
                "Invalid data",
                f"Inline data is not JSON-serializable: {str(e)}",
                suggestion="Ensure the payload only contains JSON-compatible values.",
            ),
        )

    # Build messages
    tool_name = data_type or "inline_data"
    tool_args = {"source": tool_name}

    # Extract arguments from prompt for known tools
    # Note: OpenShift queries (get_openshift_pods, get_openshift_nodes, etc.)
    # are handled by the mock MCP server, not inline data processing
    if tool_name in ["products", "users"]:
        # Extract status for products/users
        status_filter = None
        if "available" in prompt.lower() or "active" in prompt.lower():
            status_filter = "active"
            tool_args["status"] = "Active" if tool_name == "users" else "Available"
        elif "stock" in prompt.lower() or "in stock" in prompt.lower():
            status_filter = "in stock"
            tool_args["status"] = "In Stock"

        # Apply filtering
        list_key = tool_name
        if isinstance(inline_payload, dict) and list_key in inline_payload:
            items = inline_payload[list_key]
            if isinstance(items, list) and status_filter:
                filtered_items = [
                    item
                    for item in items
                    if status_filter.lower() in str(item.get("status", "")).lower()
                ]
                inline_payload[list_key] = filtered_items
                inline_data_json = json.dumps(inline_payload)
                record_count = len(filtered_items)

    messages, agent_messages = build_inline_messages(
        prompt.strip(), inline_data_json, tool_name, tool_args
    )

    movie_response = {"messages": messages}
    record_count = len(inline_payload) if isinstance(inline_payload, list) else None

    inline_data_context = {
        "source": tool_name,
        "recordCount": record_count,
        "payload": inline_payload,  # Include the actual dataset payload
    }

    return movie_response, agent_messages, inline_data_context, None

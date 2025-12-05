"""Inline data processing for generate endpoint."""

import json
from typing import Any, Optional

from utils.inline_data import build_inline_messages
from utils.logging import log_info
from utils.response import create_error_response


def process_inline_data(
    prompt: str, data: Any, data_type: Optional[str] = None
) -> tuple[Optional[dict], Optional[dict], Optional[dict]]:
    """
    Process inline data provided in the request.

    Args:
        prompt: User prompt
        data: Inline data payload
        data_type: Optional data type identifier

    Returns:
        Tuple of (movie_response, inline_data_context, error_response)
        If successful, error_response is None.
        If failed, movie_response and inline_data_context are None.
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
            create_error_response(
                "Invalid data",
                f"Inline data is not JSON-serializable: {str(e)}",
                suggestion="Ensure the payload only contains JSON-compatible values.",
            ),
        )

    # Build messages
    tool_name = data_type or "inline_data"
    tool_args = {"source": tool_name}
    messages, agent_messages = build_inline_messages(
        prompt.strip(), inline_data_json, tool_name, tool_args
    )

    movie_response = {"messages": messages}
    record_count = len(inline_payload) if isinstance(inline_payload, list) else None

    inline_data_context = {
        "source": tool_name,
        "recordCount": record_count,
    }

    return movie_response, inline_data_context, None

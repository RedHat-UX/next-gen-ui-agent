"""Inline data processing for generate endpoint."""

import json
from typing import Any, Optional, Tuple

from app.models import ErrorCode
from app.utils.logging import log_info
from app.utils.response import create_error_response
from fastapi import status
from llama_stack_client.types import ToolCall, ToolExecutionStep, ToolResponse


def process_inline_data(
    prompt: str, data: Any, data_type: Optional[str] = None
) -> Tuple[Optional[ToolExecutionStep], Optional[dict]]:
    """
    Process inline data provided in the request.

    Args:
        prompt: User prompt
        data: Inline data payload
        data_type: Optional data type identifier

    Returns:
        Tuple of (tool_step, error_response)
        If successful, error_response is None.
        If failed, tool_step is None.
    """
    log_info("Processing inline data provided in request.")

    # Accept arbitrary strings without validation
    # UI Agent Core can handle both JSON and non-JSON strings
    if isinstance(data, str):
        # Use string data as-is
        data_str = data.strip()
        if not data_str:
            return (
                None,
                create_error_response(
                    error_code=ErrorCode.INVALID_INPUT,
                    message="Invalid data",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details="Inline data string cannot be empty",
                    suggestion="Provide valid data or omit the field.",
                ),
            )
        inline_data_content = data_str
    else:
        # For non-string data (dict/list), serialize to JSON
        # If serialization fails, convert to string representation
        try:
            inline_data_content = json.dumps(data, default=str)
        except (TypeError, ValueError):
            # Fallback: use string representation
            inline_data_content = str(data)

    # Build tool call and response
    tool_name = data_type or "inline_data"
    call_id = f"{tool_name}_000"

    tool_call_args = {"description": "User-provided data"}
    if data_type:
        tool_call_args["type"] = data_type
        log_info(f"Data type: {data_type}")

    tool_call = ToolCall(call_id=call_id, tool_name=tool_name, arguments=tool_call_args)

    tool_response = ToolResponse(
        call_id=call_id, tool_name=tool_name, content=inline_data_content
    )

    tool_step = ToolExecutionStep(
        step_id="step_001",
        step_type="tool_execution",
        turn_id="turn_001",
        tool_calls=[tool_call],
        tool_responses=[tool_response],
    )

    log_info(f"Tool call: {tool_name}")
    log_info(f"Data size: {len(inline_data_content)} chars")

    return tool_step, None

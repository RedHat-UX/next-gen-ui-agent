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

    inline_payload = data

    # Handle string payload
    if isinstance(inline_payload, str):
        inline_payload = inline_payload.strip()
        if not inline_payload:
            return (
                None,
                create_error_response(
                    error_code=ErrorCode.INVALID_INPUT,
                    message="Invalid data",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details="Inline data string cannot be empty",
                    suggestion="Provide valid JSON data or omit the field.",
                ),
            )
        try:
            inline_payload = json.loads(inline_payload)
        except json.JSONDecodeError as e:
            return (
                None,
                create_error_response(
                    error_code=ErrorCode.INVALID_JSON,
                    message="Invalid data",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details=f"Inline data must be valid JSON. Parse error: {str(e)}",
                    suggestion="Provide JSON (object/array/string) that can be parsed.",
                ),
            )

    # Serialize to JSON
    try:
        inline_data_json = json.dumps(inline_payload, default=str)
    except (TypeError, ValueError) as e:
        return (
            None,
            create_error_response(
                error_code=ErrorCode.INVALID_JSON,
                message="Invalid data",
                status_code=status.HTTP_400_BAD_REQUEST,
                details=f"Inline data is not JSON-serializable: {str(e)}",
                suggestion="Ensure the payload only contains JSON-compatible values.",
            ),
        )

    # Build tool call and response
    tool_name = data_type or "inline_data"
    call_id = f"{tool_name}_000"

    tool_call_args = {"description": "User-provided data"}
    if data_type:
        tool_call_args["type"] = data_type
        log_info(f"Data type: {data_type}")

    tool_call = ToolCall(call_id=call_id, tool_name=tool_name, arguments=tool_call_args)

    tool_response = ToolResponse(
        call_id=call_id, tool_name=tool_name, content=inline_data_json
    )

    tool_step = ToolExecutionStep(
        step_id="step_001",
        step_type="tool_execution",
        turn_id="turn_001",
        tool_calls=[tool_call],
        tool_responses=[tool_response],
    )

    log_info(f"Tool call: {tool_name}")
    log_info(f"Data size: {len(inline_data_json)} chars")

    return tool_step, None

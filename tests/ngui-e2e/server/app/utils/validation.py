"""Utilities for validating and extracting data from NGUI responses."""

import json
from typing import Any, Optional, Tuple

from app.models import ErrorCode
from app.utils.logging import log_error, log_info
from app.utils.response import create_error_response
from fastapi import status


def validate_ngui_response(
    ngui_response: Any,
) -> Tuple[Optional[str], Optional[dict]]:
    """
    Validate NGUI response and extract component JSON.

    Returns:
        (component_json_str, error_response) - If validation succeeds, returns (json_str, None).
        If validation fails, returns (None, error_dict).
    """
    # Step 1: Check if response exists
    if not ngui_response:
        log_error("ERROR: NGUI response is None")
        return None, create_error_response(
            error_code=ErrorCode.NGUI_AGENT_ERROR,
            message="No UI response",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details="NGUI agent returned None",
        )

    # Step 2: Check response type
    if not isinstance(ngui_response, dict):
        log_error("ERROR: NGUI response is not a dictionary")
        return None, create_error_response(
            error_code=ErrorCode.NGUI_AGENT_ERROR,
            message="Invalid UI response format",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=f"Expected dictionary, got {type(ngui_response).__name__}",
        )

    # Step 3: Check for renditions key
    if "renditions" not in ngui_response:
        log_error("ERROR: No renditions key in NGUI response")
        return None, create_error_response(
            error_code=ErrorCode.NO_COMPONENTS_GENERATED,
            message="Missing renditions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details="NGUI response missing 'renditions' key",
        )

    # Step 4: Check renditions is not empty
    renditions = ngui_response["renditions"]
    if not renditions:
        log_error("ERROR: Empty renditions list")
        return None, create_error_response(
            error_code=ErrorCode.NO_COMPONENTS_GENERATED,
            message="No UI components generated",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details="NGUI agent returned empty renditions array",
        )

    # Step 5: Check renditions is a list
    if not isinstance(renditions, list):
        log_error("ERROR: Renditions is not a list")
        return None, create_error_response(
            error_code=ErrorCode.NO_COMPONENTS_GENERATED,
            message="Invalid renditions format",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=f"Expected list, got {type(renditions).__name__}",
        )

    # Step 6: Extract and validate rendition content
    first_rendition = renditions[0]
    log_info(f"First rendition type: {type(first_rendition)}")

    # Handle both dict and Rendition object
    if isinstance(first_rendition, dict):
        rendition_content = first_rendition.get("content")
    else:
        # Handle object with content attribute
        rendition_content = getattr(first_rendition, "content", None)

    # Step 7: Validate content exists
    if not rendition_content:
        log_error("ERROR: No content in rendition")
        return None, create_error_response(
            error_code=ErrorCode.COMPONENT_PARSING_ERROR,
            message="Empty component content",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details="Rendition missing 'content' field",
        )

    # Step 8: Validate content is string
    if not isinstance(rendition_content, str):
        log_error("ERROR: Rendition content is not a string")
        return None, create_error_response(
            error_code=ErrorCode.COMPONENT_PARSING_ERROR,
            message="Invalid content format",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=f"Expected string, got {type(rendition_content).__name__}",
        )

    # Step 9: Validate content is not empty
    if not rendition_content.strip():
        log_error("ERROR: Rendition content is empty or whitespace")
        return None, create_error_response(
            error_code=ErrorCode.COMPONENT_PARSING_ERROR,
            message="Empty component configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details="Rendition content is empty or contains only whitespace",
        )

    log_info(f"Rendition content: {rendition_content[:200]}...")

    # Step 10: Parse and validate JSON
    try:
        parsed_response = json.loads(rendition_content)
        log_info("Successfully parsed response")

        # Additional validation of parsed response
        if not isinstance(parsed_response, dict):
            return None, create_error_response(
                error_code=ErrorCode.COMPONENT_PARSING_ERROR,
                message="Invalid component configuration",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=f"Component config must be an object, got {type(parsed_response).__name__}",
            )

        if not parsed_response:
            return None, create_error_response(
                error_code=ErrorCode.COMPONENT_PARSING_ERROR,
                message="Empty component configuration",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details="Component configuration object is empty",
            )

        return rendition_content, None

    except json.JSONDecodeError as e:
        log_error(f"ERROR: Failed to parse JSON response: {e}")
        return None, create_error_response(
            error_code=ErrorCode.COMPONENT_PARSING_ERROR,
            message="Invalid JSON configuration",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=f"JSON parse error: {str(e)}",
            suggestion="The component configuration is not valid JSON",
        )


def extract_component_metadata(
    ngui_response: dict,
    model_id: str,
    base_url: str,
    tool_step: Optional[Any] = None,
    events: Optional[list] = None,
) -> dict:
    """
    Extract metadata from NGUI response for debugging and analysis.

    This function extracts useful metadata from the NGUI agent response,
    adapted for LlamaStack (vs LangGraph in the source version).

    Args:
        ngui_response: The full NGUI agent response dict
        model_id: The LLM model identifier
        base_url: The LlamaStack base URL
        tool_step: Optional ToolExecutionStep for data context
        events: Optional list of agent events for debugging

    Returns:
        Dictionary containing extracted metadata
    """
    from app.utils.agent_messages import (
        extract_tool_data_summary,
        serialize_agent_events,
    )

    metadata: dict[str, Any] = {}

    # Add model information
    metadata["model"] = {
        "model_id": model_id,
        "base_url": base_url,
    }

    # Extract rendition info
    renditions = ngui_response.get("renditions", [])
    if renditions:
        metadata["rendition_count"] = len(renditions)

        # Try to extract component type from first rendition content
        try:
            first_rendition = renditions[0]
            if isinstance(first_rendition, dict):
                content = first_rendition.get("content", "")
            else:
                content = getattr(first_rendition, "content", "")

            if content:
                parsed_content = json.loads(content)
                if "component" in parsed_content:
                    metadata["component_type"] = parsed_content["component"]
                if "title" in parsed_content:
                    metadata["component_title"] = parsed_content["title"]
        except Exception as e:
            log_error(f"Could not extract component info from rendition: {e}")

    # Add data source information
    if tool_step:
        data_summary = extract_tool_data_summary(tool_step)
        if data_summary["has_data"]:
            metadata["data_source"] = {
                "tool_name": data_summary["tool_name"],
                "data_size_bytes": data_summary["data_size"],
            }

    # Add agent events for debugging
    if events:
        metadata["agent_events"] = serialize_agent_events(events)
        metadata["event_count"] = len(events)

    return metadata

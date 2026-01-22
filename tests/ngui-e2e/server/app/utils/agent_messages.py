"""Utilities for serializing agent messages and events.

This module provides utilities to serialize LlamaStack events and messages
into a simple dictionary format for debugging and metadata purposes.

Adapted from the LangGraph version to work with LlamaStack event streams.
"""

from typing import Any


def serialize_agent_events(events: list[dict]) -> list[dict[str, Any]]:
    """
    Serialize LlamaStack agent events to a simple dict format for debugging.

    Args:
        events: List of event dictionaries from NGUI agent

    Returns:
        List of serialized event dictionaries
    """
    serialized_events = []

    for event in events:
        event_dict: dict[str, Any] = {
            "event_type": event.get("event_type", "unknown"),
        }

        # Add payload info if present
        if "payload" in event:
            payload = event["payload"]
            if isinstance(payload, dict):
                event_dict["payload_keys"] = list(payload.keys())
            elif isinstance(payload, list):
                event_dict["payload_count"] = len(payload)
            else:
                event_dict["payload_type"] = type(payload).__name__

        serialized_events.append(event_dict)

    return serialized_events


def serialize_tool_step(tool_step: Any) -> dict[str, Any]:
    """
    Serialize a LlamaStack ToolExecutionStep for debugging.

    Args:
        tool_step: ToolExecutionStep object

    Returns:
        Serialized dictionary representation
    """
    step_dict: dict[str, Any] = {
        "type": "ToolExecutionStep",
    }

    # Extract tool calls if present
    if hasattr(tool_step, "tool_calls"):
        tool_calls = tool_step.tool_calls
        if tool_calls:
            step_dict["tool_calls"] = [
                {
                    "tool_name": getattr(tc, "tool_name", "unknown"),
                    "arguments": getattr(tc, "arguments", {}),
                }
                for tc in tool_calls
            ]

    # Extract tool responses if present
    if hasattr(tool_step, "tool_responses"):
        tool_responses = tool_step.tool_responses
        if tool_responses:
            step_dict["tool_responses"] = [
                {
                    "tool_name": getattr(tr, "tool_name", "unknown"),
                    "content": str(getattr(tr, "content", ""))[
                        :200
                    ],  # Truncate for brevity
                }
                for tr in tool_responses
            ]

    return step_dict


def extract_tool_data_summary(tool_step: Any) -> dict[str, Any]:
    """
    Extract a summary of data from a ToolExecutionStep.

    Args:
        tool_step: ToolExecutionStep object

    Returns:
        Dictionary with data summary (tool name, data size, etc.)
    """
    summary: dict[str, Any] = {
        "has_data": False,
        "tool_name": None,
        "data_size": 0,
    }

    if not hasattr(tool_step, "tool_responses"):
        return summary

    tool_responses = tool_step.tool_responses
    if not tool_responses or len(tool_responses) == 0:
        return summary

    # Get first tool response
    first_response = tool_responses[0]
    summary["has_data"] = True
    summary["tool_name"] = getattr(first_response, "tool_name", "unknown")

    # Try to get data size
    content = getattr(first_response, "content", "")
    if isinstance(content, str):
        summary["data_size"] = len(content)
    elif isinstance(content, (dict, list)):
        import json

        try:
            summary["data_size"] = len(json.dumps(content))
        except Exception:
            summary["data_size"] = -1

    return summary

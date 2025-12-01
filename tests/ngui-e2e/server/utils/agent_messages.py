"""Utilities for serializing agent messages."""

from typing import Any


def serialize_agent_messages(messages: list) -> list[dict[str, Any]]:
    """
    Serialize LangChain messages to a simple dict format for debugging.

    Args:
        messages: List of LangChain message objects

    Returns:
        List of serialized message dictionaries
    """
    agent_messages = []

    for msg in messages:
        msg_dict: dict[str, Any] = {
            "type": type(msg).__name__,
            "content": str(msg.content) if hasattr(msg, "content") else str(msg),
        }

        if hasattr(msg, "tool_calls") and msg.tool_calls:
            msg_dict["tool_calls"] = [
                {"name": tc.get("name", ""), "args": tc.get("args", {})}
                for tc in msg.tool_calls
            ]

        if hasattr(msg, "name"):
            msg_dict["name"] = msg.name

        agent_messages.append(msg_dict)

    return agent_messages

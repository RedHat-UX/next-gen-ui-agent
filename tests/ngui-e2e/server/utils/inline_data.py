"""Utilities for handling inline data in requests."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def build_inline_messages(
    user_prompt: str,
    data_json: str,
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
) -> tuple[list, list]:
    """
    Build LangChain-style messages that simulate a tool call with inline data.

    Returns the messages payload expected by the NGUI agent and a simplified
    agent_messages list for debugging metadata.
    """
    call_id = f"inline_{tool_name}_1"
    tool_kwargs = tool_args or {}

    messages = [
        HumanMessage(content=user_prompt),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": tool_name,
                    "args": tool_kwargs,
                    "id": call_id,
                }
            ],
        ),
        ToolMessage(
            content=data_json,
            tool_call_id=call_id,
            name=tool_name,
        ),
    ]

    agent_messages = [
        {"type": "HumanMessage", "content": user_prompt},
        {
            "type": "AIMessage",
            "content": "",
            "tool_calls": [{"name": tool_name, "args": tool_kwargs}],
        },
        {"type": "ToolMessage", "content": data_json, "name": tool_name},
    ]

    return messages, agent_messages

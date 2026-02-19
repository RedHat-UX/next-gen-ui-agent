"""NGUI agent setup: LlamaStack (deployed) or LangGraph (local/direct LLM)."""

import json
from typing import Any

from app.config import NGUI_CONFIG, NGUI_MODEL, USE_LOCAL_LLM
from app.llm import get_llm_client, get_local_llm
from app.utils.logging import log_error, log_info
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent

# Singleton LlamaStack agent instance
_ngui_agent_instance = None

# Singleton LangGraph compiled graph (local mode)
_langgraph_graph = None
_langgraph_instance = None


async def invoke_ngui_agent(
    prompt: str,
    source_data: Any,
    source_tool_name: str,
    tool_step: Any,
) -> tuple[dict, list[dict[str, Any]], str | None, list[Any] | None]:
    """
    Invoke the configured NGUI agent (LangGraph or LlamaStack). Single entry point for generate.
    Returns (ngui_response, agent_events, error_detail, components).
    components is set for LangGraph (for debug metadata); None for LlamaStack.
    """
    agent_events: list[dict[str, Any]] = []
    if USE_LOCAL_LLM:
        from next_gen_ui_agent.types import InputData

        data_str = (
            json.dumps(source_data, default=str)
            if isinstance(source_data, (dict, list))
            else str(source_data)
        )
        backend_data = [
            InputData(
                id=f"{source_tool_name}_000", data=data_str, type=source_tool_name
            )
        ]
        graph = get_ngui_langgraph_graph()
        log_info("Calling LangGraph NGUI agent to generate UI")
        output = await graph.ainvoke(
            {"backend_data": backend_data, "user_prompt": prompt.strip()},
            config={"configurable": {"component_system": "json"}},
        )
        renditions = output.get("renditions", [])
        errors = output.get("errors", [])
        components = output.get("components", [])
        log_info(f"Generated {len(renditions)} rendition(s)")
        if not renditions and errors:
            first_error = errors[0] if errors else "LLM error"
            log_error(f"Agent produced no renditions: {first_error}")
            return ({"renditions": []}, agent_events, first_error, None)
        return ({"renditions": renditions}, agent_events, None, components)
    else:
        ngui_agent = await get_ngui_agent()
        log_info("Calling NGUI agent to generate UI")
        renditions = []
        async for event in ngui_agent.create_turn(
            user_prompt=prompt.strip(),
            steps=[tool_step],
            component_system="json",
        ):
            event_type = event.get("event_type")
            log_info(f"Event type: {event_type}")
            agent_events.append(event)
            if event_type == "rendering":
                payload = event.get("payload")
                if payload:
                    if isinstance(payload, list):
                        for item in payload:
                            if isinstance(item, dict) or hasattr(item, "content"):
                                renditions.append(item)
                    elif isinstance(payload, dict) or hasattr(payload, "content"):
                        renditions.append(payload)
            elif event_type == "success":
                ui_blocks = event.get("payload", [])
                if isinstance(ui_blocks, list):
                    for ui_block in ui_blocks:
                        r = (
                            ui_block.get("rendering")
                            if isinstance(ui_block, dict)
                            else getattr(ui_block, "rendering", None)
                        )
                        if r:
                            renditions.append(r)
                else:
                    r = (
                        ui_blocks.get("rendering")
                        if isinstance(ui_blocks, dict)
                        else getattr(ui_blocks, "rendering", None)
                    )
                    if r:
                        renditions.append(r)
            elif event_type == "error":
                error_payload = event.get("payload", {})
                log_error(f"Error event: {error_payload}")
                raise Exception(f"NGUI agent error: {error_payload}")
        log_info(f"Generated {len(renditions)} rendition(s)")
        return ({"renditions": renditions}, agent_events, None, None)


async def get_ngui_agent():
    """Get or create the NGUI agent (LlamaStack). Only valid when USE_LOCAL_LLM is False."""
    global _ngui_agent_instance
    if _ngui_agent_instance is None:
        client = get_llm_client()
        _ngui_agent_instance = NextGenUILlamaStackAgent(
            client, NGUI_MODEL, config=NGUI_CONFIG
        )
    return _ngui_agent_instance


def get_ngui_langgraph_graph():
    """Get or create the LangGraph NGUI agent (local/direct LLM). Only valid when USE_LOCAL_LLM is True."""
    global _langgraph_graph, _langgraph_instance
    if _langgraph_graph is None:
        from next_gen_ui_langgraph import NextGenUILangGraphAgent

        llm = get_local_llm()
        _langgraph_instance = NextGenUILangGraphAgent(model=llm, config=NGUI_CONFIG)
        _langgraph_graph = _langgraph_instance.build_graph()
    return _langgraph_graph

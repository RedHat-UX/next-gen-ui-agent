"""Main generate endpoint for creating UI components."""

import json
from typing import Any

from agents import ngui_agents, openshift_agent
from config import BASE_URL, MODEL, NGUI_CONFIG
from data_sources import invoke_movies_agent, process_inline_data
from fastapi import APIRouter
from models import GenerateRequest
from utils import (
    create_error_response,
    extract_component_metadata,
    log_error,
    log_info,
    validate_ngui_response,
)

router = APIRouter()


@router.post("/generate")
async def generate_response(request: GenerateRequest):
    """
    Generate UI component from user prompt.

    Supports three data sources:
    1. OpenShift agent with tools (for pod/node queries without inline data)
    2. Inline data (provided in request.data)
    3. Movies agent (fetches data from movies database)
    """
    try:
        prompt = request.prompt

        # Validate input
        if not prompt or not prompt.strip():
            return create_error_response(
                "Invalid input", "Prompt cannot be empty or whitespace only"
            )

        # Validate and select strategy
        strategy = request.strategy
        if strategy not in ngui_agents:
            return create_error_response(
                "Invalid strategy",
                f"Strategy must be 'one-step' or 'two-step', got '{strategy}'",
            )

        selected_agent = ngui_agents[strategy]
        log_info(f"=== Processing Prompt: {prompt} ===")
        log_info(f"Using strategy: {strategy}")

        # Step 1: Get data from OpenShift agent, inline source, or movies agent
        agent_messages: list[dict[str, Any]] = []
        inline_data_context: dict[str, Any] | None = None

        # Check if this is an OpenShift-related query (use tools)
        # Tool names from OpenShift agent will automatically map to InputData.type
        prompt_lower = prompt.lower()
        is_openshift_query = (
            "pod" in prompt_lower
            or "node" in prompt_lower
            or "namespace" in prompt_lower
        )

        if is_openshift_query:
            # Use OpenShift agent with tools
            log_info("Using OpenShift agent with tools...")
            openshift_response = await openshift_agent.ainvoke(
                {"messages": [{"role": "user", "content": prompt.strip()}]},
                {"recursion_limit": 10},
            )

            # Debug: Log the full response structure
            log_info(
                f"OpenShift agent response keys: {openshift_response.keys() if openshift_response else 'None'}"
            )
            if openshift_response and "messages" in openshift_response:
                log_info(f"Number of messages: {len(openshift_response['messages'])}")
                from langchain_core.messages import AIMessage, ToolMessage

                for i, msg in enumerate(openshift_response["messages"]):
                    msg_type = type(msg).__name__
                    log_info(f"Message {i}: {msg_type}")
                    if (
                        isinstance(msg, AIMessage)
                        and hasattr(msg, "tool_calls")
                        and msg.tool_calls
                    ):
                        log_info(
                            f"  Tool calls: {[tc.get('name', 'unknown') for tc in msg.tool_calls]}"
                        )
                    elif isinstance(msg, ToolMessage):
                        log_info(
                            f"  Tool message content length: {len(str(msg.content))}"
                        )

            # Extract tool messages from the agent response
            if (
                openshift_response
                and "messages" in openshift_response
                and len(openshift_response["messages"]) > 0
            ):
                # Find the last ToolMessage in the response (contains the tool result)
                from langchain_core.messages import ToolMessage

                tool_messages = [
                    msg
                    for msg in openshift_response["messages"]
                    if isinstance(msg, ToolMessage)
                ]
                if not tool_messages:
                    # Log what messages we did get
                    from langchain_core.messages import AIMessage

                    ai_messages = [
                        msg
                        for msg in openshift_response["messages"]
                        if isinstance(msg, AIMessage)
                    ]
                    if ai_messages:
                        last_ai = ai_messages[-1]
                        log_error(
                            f"Agent did not call tools. Last AI message: {last_ai.content[:200] if hasattr(last_ai, 'content') else 'N/A'}"
                        )
                    return create_error_response(
                        "Invalid response",
                        "OpenShift agent did not return tool results",
                    )

                # Use the last tool message (most recent tool call result)
                tool_result = tool_messages[-1].content
                try:
                    tool_data = json.loads(tool_result)
                    # Determine tool name from the data structure
                    if "pods" in tool_data:
                        tool_name = "get_openshift_pods"
                    elif "nodes" in tool_data:
                        tool_name = "get_openshift_nodes"
                    elif "namespaces" in tool_data:
                        tool_name = "get_openshift_namespaces"
                    else:
                        tool_name = "get_openshift_pods"  # Default fallback
                    # Use the agent's messages directly for NGUI agent
                    ngui_input = openshift_response
                    inline_data_context = {
                        "source": tool_name,
                        "recordCount": (
                            len(tool_data.get("pods", []))
                            if "pods" in tool_data
                            else (
                                len(tool_data.get("nodes", []))
                                if "nodes" in tool_data
                                else len(tool_data.get("namespaces", []))
                            )
                        ),
                        "payload": tool_data,
                    }
                    # Convert messages to agent_messages format for metadata
                    from utils.agent_messages import serialize_agent_messages

                    agent_messages = serialize_agent_messages(
                        openshift_response["messages"]
                    )
                except (json.JSONDecodeError, KeyError) as e:
                    log_error(f"Failed to parse OpenShift agent response: {e}")
                    return create_error_response(
                        "Invalid response",
                        f"OpenShift agent returned invalid data: {str(e)}",
                    )
            else:
                return create_error_response(
                    "Invalid response", "OpenShift agent returned empty response"
                )
        elif request.data is not None:
            # Process inline data (for non-OpenShift queries)
            movie_response, agent_messages, inline_data_context, error = (
                process_inline_data(prompt, request.data, request.data_type)
            )
            if error:
                return error
            ngui_input = movie_response
        else:
            # Invoke movies agent
            movie_response, agent_messages, error = invoke_movies_agent(prompt)
            if error:
                return error
            ngui_input = movie_response

        # Step 2: Pass to NGUI agent
        log_info(f"Step 2: Invoking NGUI agent with {strategy} strategy...")
        ngui_response = await selected_agent["graph"].ainvoke(ngui_input, NGUI_CONFIG)
        log_info(f"NGUI agent full response: {ngui_response}")

        # Step 3: Validate NGUI response
        component_json_str, error_response = validate_ngui_response(
            ngui_response, agent_messages
        )
        if error_response:
            return error_response

        # Step 4: Parse component JSON
        parsed_response = json.loads(component_json_str)
        log_info(f"Successfully parsed response: {parsed_response}")

        # Step 5: Extract metadata
        metadata = extract_component_metadata(
            ngui_response,
            strategy,
            MODEL,
            BASE_URL,
            inline_data_context,
            agent_messages,
        )

        if metadata:
            log_info(f"Added metadata to response: {metadata}")

        return {
            "response": parsed_response,
            "metadata": metadata,
        }

    except Exception as e:
        log_error(f"ERROR: Unexpected error in generate_response: {e}")
        import traceback

        log_error(f"Full traceback: {traceback.format_exc()}")

        # Try to include agent_messages if they were extracted before the error
        error_agent_messages = locals().get("agent_messages", None)
        return create_error_response(
            "Internal server error",
            str(e),
            None,
            "Please try again or contact support if the issue persists",
            agent_messages=error_agent_messages,
        )

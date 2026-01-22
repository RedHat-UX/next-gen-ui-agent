"""Main generate endpoint for creating UI components."""

import json
from typing import Any

from agents import ngui_agents
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

    Supports two data sources:
    1. Inline data (provided in request.data)
    2. Movies agent (fetches data from movies database)
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

        # Step 1: Get data from inline source or movies agent
        agent_messages: list[dict[str, Any]] = []
        inline_data_context: dict[str, Any] | None = None

        if request.data is not None:
            # Process inline data
            movie_response, inline_data_context, error = process_inline_data(
                prompt, request.data, request.data_type
            )
            if error:
                return error
        else:
            # Invoke movies agent
            movie_response, agent_messages, error = invoke_movies_agent(prompt)
            if error:
                return error

        # Step 2: Pass to NGUI agent
        log_info(f"Step 2: Invoking NGUI agent with {strategy} strategy...")
        ngui_response = await selected_agent["graph"].ainvoke(
            movie_response, NGUI_CONFIG
        )
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

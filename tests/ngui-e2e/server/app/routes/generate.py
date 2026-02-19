"""Main generate endpoint for creating UI components."""

import json

from app.agents import invoke_ngui_agent
from app.config import MAX_DATA_SIZE_MB, get_llm_display_info
from app.data_sources import (
    DEFAULT_DATA,
    generic_data_filter_agent,
    process_inline_data,
)
from app.llm import complete_for_filtering
from app.models import ErrorCode, GenerateRequest
from app.utils import (
    create_error_response,
    extract_component_metadata,
    log_error,
    log_info,
    log_section,
    validate_ngui_response,
)
from fastapi import APIRouter, status

router = APIRouter()


@router.post("/generate")
async def generate_response(request: GenerateRequest):
    """
    Generate UI component from user prompt.

    Supports inline data provided in request.data or uses default data.
    """
    try:
        prompt = request.prompt

        # Validate input
        if not prompt or not prompt.strip():
            return create_error_response(
                error_code=ErrorCode.INVALID_INPUT,
                message="Prompt cannot be empty or whitespace only",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        log_info(f"=== Processing Prompt: {prompt} ===")

        # Step 1: Process data
        log_info("Step 1: Processing data")

        has_data = (
            request.data is not None
            and request.data != []
            and request.data != {}
            and request.data != ""
        )

        if not has_data:
            # Use default data
            if DEFAULT_DATA is None:
                return create_error_response(
                    error_code=ErrorCode.NO_DATA_PROVIDED,
                    message="No data provided and default data is unavailable",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details="Please provide data in any supported format (JSON, CSV, text, etc.), or ensure default movies data file is available",
                    suggestion="Include 'data' field in your request with your data",
                )

            log_info("Using default data")
            source_data = DEFAULT_DATA
            source_tool_name = request.data_type or "default_data"

            # Apply filtering to default data if not skipped
            if not request.skip_filtering:
                log_info("Applying intelligent filtering to default data")
                filtered_data = await generic_data_filter_agent(
                    prompt, source_data, filter_llm_callable=complete_for_filtering
                )
                if filtered_data:
                    source_data = filtered_data
        else:
            # Use user-provided data
            log_info("Using user-provided data")
            source_data = request.data
            source_tool_name = request.data_type or "inline_data"

            # Apply filtering to user-provided data if not skipped
            if not request.skip_filtering:
                log_info("Applying intelligent filtering to user-provided data")
                filtered_data = await generic_data_filter_agent(
                    prompt, source_data, filter_llm_callable=complete_for_filtering
                )
                if filtered_data:
                    source_data = filtered_data
            else:
                log_info("Skipping filtering (skip_filtering=true)")

        # Calculate data size for validation
        # Convert to string to measure size - data can be any format
        try:
            data_str = (
                json.dumps(source_data, default=str)
                if isinstance(source_data, (dict, list))
                else str(source_data)
            )
        except (TypeError, ValueError):
            data_str = str(source_data)

        # Check data size
        size_mb = len(data_str.encode("utf-8")) / 1024 / 1024
        log_info(f"Data size: {size_mb:.2f} MB")

        if size_mb > MAX_DATA_SIZE_MB:
            return create_error_response(
                error_code=ErrorCode.DATA_TOO_LARGE,
                message="Data payload exceeds maximum size limit",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                details=f"Data size: {size_mb:.2f} MB. Maximum allowed: {MAX_DATA_SIZE_MB} MB",
            )

        # Step 2: Process inline data into tool step
        tool_step, error = process_inline_data(prompt, source_data, source_tool_name)
        if error:
            return error

        # Step 3: Invoke NGUI agent (single entry point: LangGraph or LlamaStack)
        log_section("STEP 2: INVOKING NGUI AGENT")
        try:
            ngui_response, agent_events, agent_error_detail, components = (
                await invoke_ngui_agent(
                    prompt, source_data, source_tool_name, tool_step
                )
            )
            if agent_error_detail is not None:
                return create_error_response(
                    error_code=ErrorCode.LLM_CONNECTION_ERROR,
                    message="LLM request failed; no components generated",
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    details=agent_error_detail,
                    suggestion="Check LLM_API_KEY, LLM_BASE_URL, and network access (e.g. Gemini 403 = auth failed).",
                )
        except Exception as e:
            error_msg = str(e)
            log_error(f"ERROR: NGUI agent failed: {error_msg}")
            import traceback

            log_error(f"Traceback: {traceback.format_exc()}")
            return create_error_response(
                error_code=ErrorCode.NGUI_AGENT_ERROR,
                message="Failed to generate UI components",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=error_msg,
                suggestion="Check server logs for detailed error information",
            )

        # Step 4: Validate NGUI response
        log_section("STEP 3: PROCESSING RENDITIONS")
        component_json_str, error_response = validate_ngui_response(ngui_response)
        if error_response:
            return error_response

        # Step 5: Parse component JSON
        try:
            parsed_response = json.loads(component_json_str)
            log_info(
                f"Generated component: {parsed_response.get('component')} - {parsed_response.get('title')}"
            )

            # Step 6: Extract metadata (including client debug panel fields)
            log_section("STEP 4: EXTRACTING METADATA")
            info = get_llm_display_info()
            metadata = extract_component_metadata(
                ngui_response=ngui_response,
                model_id=info["model_id"],
                base_url=info["base_url"],
                tool_step=tool_step,
                events=agent_events,
                components=components,
                strategy=request.strategy or "one-step",
            )
            log_info(f"Extracted metadata: {len(metadata)} keys")

            return {
                "response": parsed_response,
                "metadata": metadata,
            }
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse component JSON: {e}")
            return create_error_response(
                error_code=ErrorCode.COMPONENT_PARSING_ERROR,
                message="Failed to parse UI component",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=str(e),
            )

    except Exception as e:
        log_error(f"ERROR: Unexpected error in generate_response: {e}")
        import traceback

        log_error(f"Full traceback: {traceback.format_exc()}")
        return create_error_response(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
            suggestion="Please try again or contact support if the issue persists",
        )

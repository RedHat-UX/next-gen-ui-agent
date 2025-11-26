"""Prometheus data testing endpoint."""
import json

from fastapi import APIRouter
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agents import ngui_agents
from config import BASE_URL, MODEL, NGUI_CONFIG
from models import PrometheusTestRequest
from utils import (
    create_error_response,
    extract_component_metadata,
    log_error,
    log_info,
    log_section,
    validate_ngui_response,
)

router = APIRouter()


@router.post("/test-prometheus")
async def test_prometheus(request: PrometheusTestRequest):
    """
    Test endpoint for Prometheus data transformation and visualization.
    This endpoint bypasses the movies agent and directly tests the NGUI agent
    with the Prometheus input data transformer.
    """
    try:
        # Validate strategy
        strategy = request.strategy
        if strategy not in ngui_agents:
            return create_error_response(
                "Invalid strategy",
                f"Strategy must be 'one-step' or 'two-step', got '{strategy}'",
            )

        selected_agent = ngui_agents[strategy]
        log_section("Testing Prometheus Data")
        log_info(f"Strategy: {strategy}")
        log_info(f"User Prompt: {request.userPrompt}")
        log_info(f"Prometheus Data Length: {len(request.prometheusData)} characters")
        log_info(f"Downsample Factor: {request.downsample}")

        # Apply downsampling if requested
        prometheus_data = request.prometheusData
        if request.downsample and request.downsample > 1:
            try:
                prom_dict = json.loads(request.prometheusData)

                # Downsample each series' values
                if "result" in prom_dict:
                    original_count = 0
                    downsampled_count = 0

                    for series in prom_dict["result"]:
                        if "values" in series and isinstance(series["values"], list):
                            original_count += len(series["values"])
                            # Keep every Nth value
                            series["values"] = [
                                series["values"][i]
                                for i in range(
                                    0, len(series["values"]), request.downsample
                                )
                            ]
                            downsampled_count += len(series["values"])

                    log_info(
                        f"Downsampled: {original_count} → {downsampled_count} points"
                    )
                    prometheus_data = json.dumps(prom_dict)
            except Exception as e:
                log_error(f"Warning: Failed to downsample data: {e}")
                # Continue with original data

        # Create mock LangGraph messages structure with Prometheus data
        # Simulate what the movies agent would return
        messages = [
            HumanMessage(content=request.userPrompt),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_prometheus_metrics",
                        "args": {"query": "cpu_usage", "duration": "1h"},
                        "id": "call_prometheus_1",
                    }
                ],
            ),
            ToolMessage(
                content=prometheus_data,
                tool_call_id="call_prometheus_1",
                name="get_prometheus_metrics",
            ),
        ]

        mock_movie_response = {"messages": messages}

        log_info("Step 1: Invoking NGUI agent with Prometheus data...")
        ngui_response = await selected_agent["graph"].ainvoke(
            mock_movie_response, NGUI_CONFIG
        )
        log_info(f"NGUI agent response: {ngui_response}")

        # Validate response
        component_json_str, error_response = validate_ngui_response(ngui_response)
        if error_response:
            return error_response

        # Parse component JSON
        component_config = json.loads(component_json_str)

        # Extract metadata
        metadata = extract_component_metadata(
            ngui_response, strategy, MODEL, BASE_URL
        )

        log_info("✓ Successfully generated UI component")
        return {
            "response": component_config,
            "metadata": metadata,
        }

    except Exception as e:
        log_section("PROMETHEUS TEST ERROR")
        log_error(f"Error Type: {type(e).__name__}")
        log_error(f"Error Message: {str(e)}")
        import traceback

        log_error(f"Full traceback: {traceback.format_exc()}")
        return create_error_response(
            "Prometheus test error", f"Failed to process Prometheus data: {str(e)}"
        )


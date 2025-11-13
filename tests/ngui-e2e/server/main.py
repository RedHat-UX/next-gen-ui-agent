import json
import logging
import os
from typing import Any, Optional

import httpx
import urllib3
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_agent.agent_config import AgentConfig
from next_gen_ui_agent.types import AgentConfigDataType
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent
from next_gen_ui_testing.data_set_movies import get_all_movies, search_movie
from pydantic import BaseModel, Field, SecretStr

# Load environment variables
load_dotenv()

# Configure logging to show INFO level messages from next_gen_ui_agent
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Set next_gen_ui_agent logger to INFO level
logging.getLogger("next_gen_ui_agent").setLevel(logging.INFO)

# Validate required environment variables
required_env_vars = ["LLM_MODEL", "LLM_BASE_URL"]
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")

# === Setup ===
# Configuration loaded from environment variables
model = os.getenv("LLM_MODEL", "llama3.2:3b")
base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
api_key = os.getenv("LLM_API_KEY")

# Debug logging for LLM configuration
print("\n" + "=" * 60)
print("LLM CONFIGURATION DEBUG")
print("=" * 60)
print(f"Model: {model}")
print(f"Base URL: {base_url}")
print(f"API Key: {'SET (length=' + str(len(api_key)) + ')' if api_key else 'NOT SET'}")
print("=" * 60 + "\n")

# Initialize ChatOpenAI with proper argument types
# Note: Setting http_client for SSL compatibility with corporate APIs

# Suppress SSL warnings for internal corporate APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create BOTH sync and async httpx clients with SSL verification disabled
# (LangChain uses sync for invoke() and async for ainvoke())
sync_client = httpx.Client(verify=False, timeout=60.0)
async_client = httpx.AsyncClient(verify=False, timeout=60.0)

# For Ollama and similar local LLMs, a dummy API key is acceptable
if not api_key:
    api_key = "ollama"

llm = ChatOpenAI(
    model=model,
    base_url=base_url,
    api_key=SecretStr(api_key),
    http_client=sync_client,
    http_async_client=async_client,
)

# Test the connection
print("Testing LLM connection...")
try:
    test_response = llm.invoke("test")
    print(f"✓ LLM connection successful! Response type: {type(test_response)}")
except Exception as e:
    print("✗ LLM connection FAILED!")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {str(e)}")
    print(f"  Full error: {repr(e)}")

    # Try to get more details from the exception
    import traceback

    print("\nFull traceback:")
    traceback.print_exc()

    # Check for underlying cause
    if hasattr(e, "__cause__") and e.__cause__:
        print(f"\nUnderlying cause: {type(e.__cause__).__name__}: {e.__cause__}")

    # Check for response attribute
    if hasattr(e, "response"):
        print("\nHTTP Response details:")
        print(f"  Status: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"  Headers: {getattr(e.response, 'headers', 'N/A')}")
        print(f"  Body: {getattr(e.response, 'text', 'N/A')[:1000]}")

    print("\nThis may cause failures when processing requests.\n")

# Important: use the tool function directly (not call it)
movies_agent = create_react_agent(
    model=llm,
    tools=[
        search_movie,
        get_all_movies,
    ],
    prompt="""You are a helpful movies assistant. Use the available tools to answer user questions.

TOOL SELECTION:
- For a specific movie by name → search_movie(title="Movie Name")
- For all other queries → get_all_movies() with optional filters

FILTERING with get_all_movies():
The get_all_movies tool supports these filters:
- director: Filter by director name (e.g., director="Christopher Nolan")
- genre: Filter by genre (e.g., genre="Sci-Fi")
- actor: Filter by actor name (e.g., actor="Tom Hanks")
- year: Filter by exact year (e.g., year=2008)
- min_year: Movies released on or after year (e.g., min_year=2000)
- max_year: Movies released on or before year (e.g., max_year=2010)
- min_rating: Movies with IMDB rating >= value (e.g., min_rating=8.5)

IMPORTANT ROLE CLARIFICATION:
You are a DATA FETCHING agent, not a visualization/display agent.
- Your job: Fetch movie data from the database (including poster URLs, trailer URLs, etc.)
- NOT your job: Create charts, tables, visualizations, or display images (another system handles that)
- When asked for posters/images/trailers: Fetch the data with URLs - the downstream system will display them

POSTER/IMAGE/VIDEO REQUESTS:
When user asks to "show poster", "display image", "play trailer", etc:
→ Call the appropriate tool to fetch the movie data (which includes poster/trailer URLs)
→ Return the data with URLs
→ Do NOT say "I cannot display" - you CAN fetch the URLs, and the NGUI agent will handle display

DEFAULT BEHAVIOR:
When the user asks to visualize, display, show, or compare data WITHOUT specifying particular movies:
→ Call get_all_movies() with NO filters
→ Do NOT ask "which movies?" or "what criteria?"
→ Let the downstream visualization system decide what to show

Examples of requests that should fetch ALL movies:
- "show as a chart/table/cards"
- "compare ratings/revenue/etc"
- "distribution of genres/directors"
- "visualize the data"
- Any request about displaying or analyzing movies in general

Only apply filters when user EXPLICITLY mentions specific criteria:
- "Christopher Nolan movies" → filter by director
- "movies from 2010" → filter by year
- "action movies" → filter by genre

Examples:
- "Christopher Nolan movies" → get_all_movies(director="Christopher Nolan")
- "Action films" → get_all_movies(genre="Action")
- "Movies from 2008" → get_all_movies(year=2008)
- "Tom Hanks movies" → get_all_movies(actor="Tom Hanks")
- "Highly rated Sci-Fi" → get_all_movies(genre="Sci-Fi", min_rating=8.0)
- "All movies" → get_all_movies()

IMPORTANT: Call get_all_movies ONCE with appropriate filters, then return the results.

Available data: revenue, budget, profit, ROI, ratings, awards, genres, directors, actors, opening weekend, weekly box office.""",
)

# Create both agent instances with different strategies
# Configure data types with transformers

# Map get_prometheus_metrics tool calls to use prometheus transformer
data_types_config = {
    "get_prometheus_metrics": AgentConfigDataType(
        data_transformer="prometheus",
    )
}

# One-step strategy agent
config_onestep = AgentConfig(
    component_selection_strategy="one_llm_call",
    unsupported_components=True,
    data_types=data_types_config,
)
ngui_agent_onestep_instance = NextGenUILangGraphAgent(model=llm, config=config_onestep)
ngui_agent_onestep = ngui_agent_onestep_instance.build_graph()

# Two-step strategy agent
config_twostep = AgentConfig(
    component_selection_strategy="two_llm_calls",
    unsupported_components=True,
    data_types=data_types_config,
)
ngui_agent_twostep_instance = NextGenUILangGraphAgent(model=llm, config=config_twostep)
ngui_agent_twostep = ngui_agent_twostep_instance.build_graph()

# Store agents in a dictionary for easy access
ngui_agents = {
    "one-step": {
        "instance": ngui_agent_onestep_instance,
        "graph": ngui_agent_onestep,
    },
    "two-step": {
        "instance": ngui_agent_twostep_instance,
        "graph": ngui_agent_twostep,
    },
}

ngui_cfg = {
    "configurable": {
        "component_system": "json",
        "unsupported_components": True,  # Enable experimental components like chart, table, set-of-cards
    }
}

# === FastAPI setup ===
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str
    strategy: Optional[str] = Field(
        default="one-step",
        description="Component selection strategy: 'one-step' or 'two-step'",
    )


def create_error_response(
    error: str,
    details: str,
    raw_response: Optional[Any] = None,
    suggestion: Optional[str] = None,
    agent_messages: Optional[list] = None,
) -> dict:
    """Helper function to create standardized error responses."""
    response = {
        "error": error,
        "details": details,
    }

    if raw_response is not None:
        response["raw_response"] = str(raw_response)

    if suggestion:
        response["suggestion"] = suggestion

    # Add agent messages to metadata for debugging
    if agent_messages:
        response["metadata"] = {"agentMessages": agent_messages}

    return response


@app.get("/health")
async def health_check():
    """Health check endpoint to verify server and Ollama connectivity."""
    try:
        # Test Ollama connection
        _ = llm.invoke("test")
        return {
            "status": "healthy",
            "ollama_connected": True,
            "model": model,
            "base_url": base_url,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_connected": False,
            "error": str(e),
            "model": model,
            "base_url": base_url,
        }


@app.get("/model-info")
async def get_model_info():
    """Get information about the connected LLM model."""
    return {
        "name": model,
        "baseUrl": base_url,
    }


class PrometheusTestRequest(BaseModel):
    prometheusData: str = Field(
        ..., description="Prometheus query_range result as JSON string"
    )
    userPrompt: str = Field(
        default="Show time-series data", description="User prompt for UI generation"
    )
    strategy: Optional[str] = Field(
        default="one-step",
        description="Component selection strategy: 'one-step' or 'two-step'",
    )
    downsample: Optional[int] = Field(
        default=1,
        description="Downsample factor: 1 = all points, 2 = every other point, etc.",
    )


@app.post("/test-prometheus")
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
        print("\n=== Testing Prometheus Data ===")
        print(f"Strategy: {strategy}")
        print(f"User Prompt: {request.userPrompt}")
        print(f"Prometheus Data Length: {len(request.prometheusData)} characters")
        print(f"Downsample Factor: {request.downsample}")

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

                    print(f"Downsampled: {original_count} → {downsampled_count} points")
                    prometheus_data = json.dumps(prom_dict)
            except Exception as e:
                print(f"Warning: Failed to downsample data: {e}")
                # Continue with original data

        # Create mock LangGraph messages structure with Prometheus data
        # Simulate what the movies agent would return
        from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

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

        print("Step 1: Invoking NGUI agent with Prometheus data...")
        ngui_response = await selected_agent["graph"].ainvoke(
            mock_movie_response, ngui_cfg
        )
        print(f"NGUI agent response: {ngui_response}")

        # Validate response
        if not ngui_response:
            return create_error_response(
                "No UI response", "NGUI agent returned None", ngui_response
            )

        if not isinstance(ngui_response, dict):
            return create_error_response(
                "Invalid response type",
                f"Expected dict, got {type(ngui_response).__name__}",
                ngui_response,
            )

        renditions = ngui_response.get("renditions", [])
        if not renditions or len(renditions) == 0:
            return create_error_response(
                "No UI components generated",
                "NGUI agent returned empty renditions array",
                ngui_response,
            )

        # Extract first component
        first_rendition = renditions[0]
        component_json_str = first_rendition.content

        try:
            component_config = json.loads(component_json_str)
        except json.JSONDecodeError as e:
            return create_error_response(
                "Invalid JSON",
                f"Could not parse component JSON: {str(e)}",
                {"raw": component_json_str},
            )

        # Extract metadata
        metadata = {}
        if "components" in ngui_response and len(ngui_response["components"]) > 0:
            first_component = ngui_response["components"][0]

            if hasattr(first_component, "reasonForTheComponentSelection"):
                metadata["reason"] = first_component.reasonForTheComponentSelection
            if hasattr(first_component, "confidenceScore"):
                metadata["confidence"] = first_component.confidenceScore
            if hasattr(first_component, "component"):
                metadata["componentType"] = first_component.component

            metadata["strategy"] = strategy

            # Extract LLM interactions if available
            if (
                hasattr(first_component, "llm_interactions")
                and first_component.llm_interactions
            ):
                metadata["llmInteractions"] = first_component.llm_interactions

            # Extract data transformation info
            if hasattr(first_component, "input_data_transformer_name"):
                metadata["dataTransform"] = {
                    "transformerName": first_component.input_data_transformer_name,
                    "jsonWrappingField": getattr(
                        first_component, "json_wrapping_field_name", None
                    ),
                }

        print("✓ Successfully generated UI component")
        return {
            "response": component_config,
            "metadata": {**metadata, "model": {"name": model, "baseUrl": base_url}},
        }

    except Exception as e:
        print("\n" + "=" * 60)
        print("PROMETHEUS TEST ERROR")
        print("=" * 60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("=" * 60 + "\n")
        import traceback

        traceback.print_exc()
        return create_error_response(
            "Prometheus test error", f"Failed to process Prometheus data: {str(e)}"
        )


@app.post("/generate")
async def generate_response(request: GenerateRequest):
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
        print(f"=== Processing Prompt: {prompt} ===")
        print(f"Using strategy: {strategy}")

        print("Step 1: Invoking movies agent...")
        try:
            movie_response = movies_agent.invoke(
                {"messages": [{"role": "user", "content": prompt.strip()}]},
                {"recursion_limit": 10},  # Allow the agent to run tool execution steps
            )
            print(f"Movies agent response: {movie_response}")
            print(f"Number of messages: {len(movie_response.get('messages', []))}")
            for i, msg in enumerate(movie_response.get("messages", [])):
                print(
                    f"Message {i}: Type={type(msg).__name__}, Content preview={str(msg)[:200]}"
                )

            # Validate movie response
            if not movie_response or not movie_response.get("messages"):
                return create_error_response(
                    "Movies agent failed",
                    "Movies agent returned empty or invalid response",
                    movie_response,
                )

            # Extract agent messages immediately for debugging (so they're available even if errors occur later)
            agent_messages = []
            try:
                messages = movie_response.get("messages", [])
                for msg in messages:
                    msg_dict = {
                        "type": type(msg).__name__,
                        "content": str(msg.content)
                        if hasattr(msg, "content")
                        else str(msg),
                    }
                    # Add additional attributes for specific message types
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        msg_dict["tool_calls"] = [
                            {"name": tc.get("name", ""), "args": tc.get("args", {})}
                            for tc in msg.tool_calls
                        ]
                    if hasattr(msg, "name"):
                        msg_dict["name"] = msg.name
                    agent_messages.append(msg_dict)
            except Exception as e:
                print(f"Warning: Could not serialize agent messages: {e}")

        except Exception as e:
            print("\n" + "=" * 60)
            print("MOVIES AGENT ERROR DEBUG")
            print("=" * 60)
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"Full Error: {repr(e)}")
            if hasattr(e, "__cause__"):
                print(f"Caused by: {e.__cause__}")
            if hasattr(e, "response"):
                print(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
                print(f"Response text: {getattr(e.response, 'text', 'N/A')[:500]}")
            print(f"{'='*60}\n")
            return create_error_response(
                "Movies agent error", f"Failed to get movie information: {str(e)}"
            )

        # Step 2: Pass to Next Gen UI agent
        print(f"Step 2: Invoking NGUI agent with {strategy} strategy...")
        ngui_response = await selected_agent["graph"].ainvoke(movie_response, ngui_cfg)
        print(f"NGUI agent full response: {ngui_response}")

        # Step 3: Comprehensive validation of NGUI response
        if not ngui_response:
            print("ERROR: NGUI response is None")
            return create_error_response(
                "No UI response",
                "NGUI agent returned None",
                ngui_response,
                agent_messages=agent_messages,
            )

        if not isinstance(ngui_response, dict):
            print("ERROR: NGUI response is not a dictionary")
            return create_error_response(
                "Invalid UI response format",
                f"Expected dictionary, got {type(ngui_response).__name__}",
                ngui_response,
                agent_messages=agent_messages,
            )

        if "renditions" not in ngui_response:
            print("ERROR: No renditions key in NGUI response")
            return create_error_response(
                "Missing renditions",
                "NGUI response missing 'renditions' key",
                ngui_response,
                agent_messages=agent_messages,
            )

        renditions = ngui_response["renditions"]
        if not renditions:
            print("ERROR: Empty renditions list")
            return create_error_response(
                "No UI components generated",
                "NGUI agent returned empty renditions array",
                agent_messages=agent_messages,
            )

        if not isinstance(renditions, list):
            print("ERROR: Renditions is not a list")
            return create_error_response(
                "Invalid renditions format",
                f"Expected list, got {type(renditions).__name__}",
                ngui_response,
                agent_messages=agent_messages,
            )

        # Step 4: Extract and validate rendition content
        first_rendition = renditions[0]
        print(f"First rendition type: {type(first_rendition)}")
        print(f"First rendition: {first_rendition}")

        # Handle both dict and Rendition object
        if isinstance(first_rendition, dict):
            rendition_content = first_rendition.get("content")
            print(f"Extracted content from dict: {rendition_content}")
        else:
            # Handle LangGraph Rendition object
            try:
                rendition_content = getattr(first_rendition, "content", None)
                print(f"Extracted content from object attribute: {rendition_content}")

                if rendition_content is None:
                    # Try to access as string representation
                    rendition_str = str(first_rendition)
                    print(f"Rendition as string: {rendition_str}")

                    # Extract content from string representation
                    import re

                    content_match = re.search(r"content='([^']*)'", rendition_str)
                    if content_match:
                        rendition_content = content_match.group(1)
                        print(f"Extracted content from regex: {rendition_content}")
                    else:
                        print("ERROR: Could not extract content from rendition string")
                        return create_error_response(
                            "Invalid rendition content",
                            "Could not extract content from rendition object",
                            first_rendition,
                            agent_messages=agent_messages,
                        )
            except Exception as e:
                print(f"ERROR: Failed to extract content from rendition: {e}")
                return create_error_response(
                    "Invalid rendition format",
                    f"Failed to extract content from rendition object: {str(e)}",
                    first_rendition,
                    agent_messages=agent_messages,
                )
        if not rendition_content:
            print("ERROR: No content in rendition")
            return create_error_response(
                "Empty component content",
                "Rendition missing 'content' field",
                first_rendition,
                agent_messages=agent_messages,
            )

        if not isinstance(rendition_content, str):
            print("ERROR: Rendition content is not a string")
            return create_error_response(
                "Invalid content format",
                f"Expected string, got {type(rendition_content).__name__}",
                rendition_content,
                agent_messages=agent_messages,
            )

        if not rendition_content.strip():
            print("ERROR: Rendition content is empty or whitespace")
            return create_error_response(
                "Empty component configuration",
                "Rendition content is empty or contains only whitespace",
                rendition_content,
                agent_messages=agent_messages,
            )

        print(f"Rendition content: {rendition_content}")

        # Step 5: Parse JSON with comprehensive error handling
        try:
            parsed_response = json.loads(rendition_content)
            print(f"Successfully parsed response: {parsed_response}")

            # Additional validation of parsed response
            if not isinstance(parsed_response, dict):
                return create_error_response(
                    "Invalid component configuration",
                    f"Component config must be an object, got {type(parsed_response).__name__}",
                    rendition_content,
                )

            if not parsed_response:
                return create_error_response(
                    "Empty component configuration",
                    "Component configuration object is empty",
                    rendition_content,
                )

            # Add component metadata (reasoning, confidence) for debug mode
            response_with_metadata = {"response": parsed_response}

            # Extract component metadata if available
            components = ngui_response.get("components", [])
            if components and len(components) > 0:
                first_component = components[0]
                metadata = {}

                # Add reasoning and confidence if available
                if hasattr(first_component, "reasonForTheComponentSelection"):
                    metadata["reason"] = first_component.reasonForTheComponentSelection
                if hasattr(first_component, "confidenceScore"):
                    metadata["confidence"] = first_component.confidenceScore
                if hasattr(first_component, "component"):
                    metadata["componentType"] = first_component.component

                # Add model information
                metadata["model"] = {"name": model, "baseUrl": base_url}

                # Add component selection strategy information
                metadata["strategy"] = strategy

                # Add data transformation information
                data_transform = {}
                if (
                    hasattr(first_component, "input_data_transformer_name")
                    and first_component.input_data_transformer_name
                ):
                    data_transform[
                        "transformerName"
                    ] = first_component.input_data_transformer_name
                if (
                    hasattr(first_component, "json_wrapping_field_name")
                    and first_component.json_wrapping_field_name
                ):
                    data_transform[
                        "jsonWrappingField"
                    ] = first_component.json_wrapping_field_name
                if hasattr(first_component, "fields") and first_component.fields:
                    data_transform["fieldCount"] = len(first_component.fields)
                    data_transform["fields"] = [
                        {"name": field.name, "dataPath": field.data_path}
                        for field in first_component.fields
                    ]
                if hasattr(first_component, "chartType") and first_component.chartType:
                    data_transform["chartType"] = first_component.chartType
                if data_transform:
                    metadata["dataTransform"] = data_transform

                # Add LLM interaction history for debugging
                if (
                    hasattr(first_component, "llm_interactions")
                    and first_component.llm_interactions
                ):
                    metadata["llmInteractions"] = first_component.llm_interactions

                # Add agent messages for debugging (already extracted earlier)
                if agent_messages:
                    metadata["agentMessages"] = agent_messages

                if metadata:
                    response_with_metadata["metadata"] = metadata
                    print(f"Added metadata to response: {metadata}")

            return response_with_metadata

        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
            return create_error_response(
                "Invalid JSON configuration",
                f"JSON parse error: {str(e)}",
                rendition_content,
                "The component configuration is not valid JSON",
                agent_messages=agent_messages,
            )

    except Exception as e:
        print(f"ERROR: Unexpected error in generate_response: {e}")
        import traceback

        print(f"Full traceback: {traceback.format_exc()}")
        # Try to include agent_messages if they were extracted before the error
        error_agent_messages = locals().get("agent_messages", None)
        return create_error_response(
            "Internal server error",
            str(e),
            None,
            "Please try again or contact support if the issue persists",
            agent_messages=error_agent_messages,
        )

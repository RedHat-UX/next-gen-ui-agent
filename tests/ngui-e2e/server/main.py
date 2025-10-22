import json
import os
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent
from next_gen_ui_langgraph.readme_example import (
    compare_movies,
    get_box_office_leaders,
    get_pixar_movies,
    get_top_rated_movies,
    search_movie,
)
from pydantic import BaseModel, SecretStr

# Load environment variables
load_dotenv()

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

# Initialize ChatOpenAI with proper argument types
if api_key:
    llm = ChatOpenAI(model=model, base_url=base_url, api_key=SecretStr(api_key))
else:
    llm = ChatOpenAI(model=model, base_url=base_url)

# Important: use the tool function directly (not call it)
movies_agent = create_react_agent(
    model=llm,
    tools=[
        search_movie,
        get_pixar_movies,
        get_top_rated_movies,
        compare_movies,
        get_box_office_leaders,
    ],
    prompt="You are a helpful movies assistant. Use the available tools to answer user questions about movies, ratings, and box office performance.",
)

ngui_agent = NextGenUILangGraphAgent(model=llm).build_graph()
ngui_cfg = {"configurable": {"component_system": "json"}}

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


def create_error_response(
    error: str,
    details: str,
    raw_response: Optional[Any] = None,
    suggestion: Optional[str] = None,
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

    return response


@app.post("/generate")
async def generate_response(request: GenerateRequest):
    try:
        prompt = request.prompt

        # Validate input
        if not prompt or not prompt.strip():
            return create_error_response(
                "Invalid input", "Prompt cannot be empty or whitespace only"
            )

        print(f"=== Processing Prompt: {prompt} ===")

        # Step 1: Invoke movies agent with error handling
        print("Step 1: Invoking movies agent...")
        try:
            movie_response = movies_agent.invoke(
                {"messages": [{"role": "user", "content": prompt.strip()}]}
            )
            print(f"Movies agent response: {movie_response}")

            # Validate movie response
            if not movie_response or not movie_response.get("messages"):
                return create_error_response(
                    "Movies agent failed",
                    "Movies agent returned empty or invalid response",
                    movie_response,
                )

        except Exception as e:
            print(f"ERROR: Movies agent failed: {e}")
            return create_error_response(
                "Movies agent error", f"Failed to get movie information: {str(e)}"
            )

        # Step 2: Pass to Next Gen UI agent
        print("Step 2: Invoking NGUI agent...")
        ngui_response = await ngui_agent.ainvoke(movie_response, ngui_cfg)
        print(f"NGUI agent full response: {ngui_response}")

        # Step 3: Comprehensive validation of NGUI response
        if not ngui_response:
            print("ERROR: NGUI response is None")
            return create_error_response(
                "No UI response", "NGUI agent returned None", ngui_response
            )

        if not isinstance(ngui_response, dict):
            print("ERROR: NGUI response is not a dictionary")
            return create_error_response(
                "Invalid UI response format",
                f"Expected dictionary, got {type(ngui_response).__name__}",
                ngui_response,
            )

        if "renditions" not in ngui_response:
            print("ERROR: No renditions key in NGUI response")
            return create_error_response(
                "Missing renditions",
                "NGUI response missing 'renditions' key",
                ngui_response,
            )

        renditions = ngui_response["renditions"]
        if not renditions:
            print("ERROR: Empty renditions list")
            return create_error_response(
                "No UI components generated",
                "NGUI agent returned empty renditions array",
            )

        if not isinstance(renditions, list):
            print("ERROR: Renditions is not a list")
            return create_error_response(
                "Invalid renditions format",
                f"Expected list, got {type(renditions).__name__}",
                ngui_response,
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
                        )
            except Exception as e:
                print(f"ERROR: Failed to extract content from rendition: {e}")
                return create_error_response(
                    "Invalid rendition format",
                    f"Failed to extract content from rendition object: {str(e)}",
                    first_rendition,
                )
        if not rendition_content:
            print("ERROR: No content in rendition")
            return create_error_response(
                "Empty component content",
                "Rendition missing 'content' field",
                first_rendition,
            )

        if not isinstance(rendition_content, str):
            print("ERROR: Rendition content is not a string")
            return create_error_response(
                "Invalid content format",
                f"Expected string, got {type(rendition_content).__name__}",
                rendition_content,
            )

        if not rendition_content.strip():
            print("ERROR: Rendition content is empty or whitespace")
            return create_error_response(
                "Empty component configuration",
                "Rendition content is empty or contains only whitespace",
                rendition_content,
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

            return {"response": parsed_response}

        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
            return create_error_response(
                "Invalid JSON configuration",
                f"JSON parse error: {str(e)}",
                rendition_content,
                "The component configuration is not valid JSON",
            )

    except Exception as e:
        print(f"ERROR: Unexpected error in generate_response: {e}")
        import traceback

        print(f"Full traceback: {traceback.format_exc()}")
        return create_error_response(
            "Internal server error",
            str(e),
            None,
            "Please try again or contact support if the issue persists",
        )

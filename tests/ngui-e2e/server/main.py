import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent
from next_gen_ui_langgraph.readme_example import search_movie
from pydantic import BaseModel

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
    llm = ChatOpenAI(model=model, base_url=base_url, api_key=api_key)
else:
    llm = ChatOpenAI(model=model, base_url=base_url)

# Important: use the tool function directly (not call it)
movies_agent = create_react_agent(
    model=llm,
    tools=[search_movie],
    prompt="You are useful movies assistant to answer user questions",
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


@app.post("/generate")
async def generate_response(request: GenerateRequest):
    try:
        prompt = request.prompt

        # Validate input
        if not prompt or not prompt.strip():
            return {
                "error": "Invalid input",
                "details": "Prompt cannot be empty or whitespace only",
            }

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
                return {
                    "error": "Movies agent failed",
                    "details": "Movies agent returned empty or invalid response",
                    "raw_response": str(movie_response),
                }

        except Exception as e:
            print(f"ERROR: Movies agent failed: {e}")
            return {
                "error": "Movies agent error",
                "details": f"Failed to get movie information: {str(e)}",
                "type": type(e).__name__,
            }

        # Step 2: Pass to Next Gen UI agent
        print("Step 2: Invoking NGUI agent...")
        ngui_response = await ngui_agent.ainvoke(movie_response, ngui_cfg)
        print(f"NGUI agent full response: {ngui_response}")

        # Step 3: Comprehensive validation of NGUI response
        if not ngui_response:
            print("ERROR: NGUI response is None")
            return {
                "error": "No UI response",
                "details": "NGUI agent returned None",
                "raw_response": str(ngui_response),
            }

        if not isinstance(ngui_response, dict):
            print("ERROR: NGUI response is not a dictionary")
            return {
                "error": "Invalid UI response format",
                "details": f"Expected dictionary, got {type(ngui_response).__name__}",
                "raw_response": str(ngui_response),
            }

        if "renditions" not in ngui_response:
            print("ERROR: No renditions key in NGUI response")
            return {
                "error": "Missing renditions",
                "details": "NGUI response missing 'renditions' key",
                "raw_response": str(ngui_response),
            }

        renditions = ngui_response["renditions"]
        if not renditions:
            print("ERROR: Empty renditions list")
            return {
                "error": "No UI components generated",
                "details": "NGUI agent returned empty renditions array",
            }

        if not isinstance(renditions, list):
            print("ERROR: Renditions is not a list")
            return {
                "error": "Invalid renditions format",
                "details": f"Expected list, got {type(renditions).__name__}",
                "raw_response": str(ngui_response),
            }

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
                        return {
                            "error": "Invalid rendition content",
                            "details": "Could not extract content from rendition object",
                            "raw_response": str(first_rendition),
                        }
            except Exception as e:
                print(f"ERROR: Failed to extract content from rendition: {e}")
                return {
                    "error": "Invalid rendition format",
                    "details": f"Failed to extract content from rendition object: {str(e)}",
                    "raw_response": str(first_rendition),
                }
        if not rendition_content:
            print("ERROR: No content in rendition")
            return {
                "error": "Empty component content",
                "details": "Rendition missing 'content' field",
                "raw_response": str(first_rendition),
            }

        if not isinstance(rendition_content, str):
            print("ERROR: Rendition content is not a string")
            return {
                "error": "Invalid content format",
                "details": f"Expected string, got {type(rendition_content).__name__}",
                "raw_response": str(rendition_content),
            }

        if not rendition_content.strip():
            print("ERROR: Rendition content is empty or whitespace")
            return {
                "error": "Empty component configuration",
                "details": "Rendition content is empty or contains only whitespace",
                "raw_response": rendition_content,
            }

        print(f"Rendition content: {rendition_content}")

        # Step 5: Parse JSON with comprehensive error handling
        try:
            parsed_response = json.loads(rendition_content)
            print(f"Successfully parsed response: {parsed_response}")

            # Additional validation of parsed response
            if not isinstance(parsed_response, dict):
                return {
                    "error": "Invalid component configuration",
                    "details": f"Component config must be an object, got {type(parsed_response).__name__}",
                    "raw_content": rendition_content,
                }

            if not parsed_response:
                return {
                    "error": "Empty component configuration",
                    "details": "Component configuration object is empty",
                    "raw_content": rendition_content,
                }

            return {"response": parsed_response}

        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
            return {
                "error": "Invalid JSON configuration",
                "details": f"JSON parse error: {str(e)}",
                "raw_content": rendition_content,
                "suggestion": "The component configuration is not valid JSON",
            }

    except Exception as e:
        print(f"ERROR: Unexpected error in generate_response: {e}")
        import traceback

        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": "Internal server error",
            "details": str(e),
            "type": type(e).__name__,
            "suggestion": "Please try again or contact support if the issue persists",
        }

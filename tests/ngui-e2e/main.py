import json

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent
from next_gen_ui_langgraph.readme_example import search_movie
from pydantic import BaseModel

# === Setup ===
# Use llama3.2:3b for better field mapping
llm = ChatOpenAI(model="llama3.2:3b", base_url="http://localhost:11434/v1")

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
        print(f"=== Processing Prompt: {prompt} ===")

        # Step 1: Invoke movies agent
        print("Step 1: Invoking movies agent...")
        movie_response = movies_agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": prompt or "Give me details of toy story"}
                ]
            }
        )
        print(f"Movies agent response: {movie_response}")

        # Step 2: Pass to Next Gen UI agent
        print("Step 2: Invoking NGUI agent...")
        ngui_response = await ngui_agent.ainvoke(movie_response, ngui_cfg)
        print(f"NGUI agent full response: {ngui_response}")

        # Step 3: Check if renditions exist and are not empty
        if not ngui_response.get("renditions"):
            print("ERROR: No renditions found in NGUI response")
            return {
                "error": "No UI components generated",
                "details": "NGUI agent failed to generate any renditions",
                "raw_response": str(ngui_response)
            }
        
        if len(ngui_response["renditions"]) == 0:
            print("ERROR: Empty renditions list")
            return {
                "error": "Empty renditions list", 
                "details": "NGUI agent returned empty renditions array",
                "raw_response": str(ngui_response)
            }

        # Step 4: Extract and parse the response
        rendition_content = ngui_response["renditions"][0].content
        print(f"Rendition content: {rendition_content}")
        
        try:
            parsed_response = json.loads(rendition_content)
            print(f"Successfully parsed response: {parsed_response}")
            return {"response": parsed_response}
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON response: {e}")
            return {
                "error": "Invalid JSON response",
                "details": f"JSON parse error: {str(e)}",
                "raw_content": rendition_content
            }

    except Exception as e:
        print(f"ERROR: Unexpected error in generate_response: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "error": "Internal server error",
            "details": str(e),
            "type": type(e).__name__
        }


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")

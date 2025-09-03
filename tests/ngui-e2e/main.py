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
llm = ChatOpenAI(model="granite3-dense:8b", base_url="http://localhost:11434/v1")

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
    prompt = request.prompt
    print("Prompt === " + prompt)

    # Step 1: Invoke movies agent
    movie_response = movies_agent.invoke(
        {
            "messages": [
                {"role": "user", "content": prompt or "Give me details of toy story"}
            ]
        }
    )

    # Step 2: Pass to Next Gen UI agent
    ngui_response = await ngui_agent.ainvoke(movie_response, ngui_cfg)

    print(ngui_response["renditions"][0].content)

    # Step 3: Return UI response
    return {"response": json.loads(ngui_response["renditions"][0].content)}


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")

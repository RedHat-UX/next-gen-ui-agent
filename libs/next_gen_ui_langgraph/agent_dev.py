# type: ignore

from agent import NextGenUILangGraphAgent  # pants: no-infer-dep
from langchain_openai import ChatOpenAI

llm_settings = {
    "model": "llama3.2",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "temperature": 0,
}
llm = ChatOpenAI(**llm_settings, disable_streaming=True)

agent = NextGenUILangGraphAgent(model=llm)

graph = agent.build_graph()

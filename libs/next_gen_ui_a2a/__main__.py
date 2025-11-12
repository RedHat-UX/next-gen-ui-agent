import logging
import os

import uvicorn  # pants: no-infer-dep
from a2a.server.apps import A2AStarletteApplication  # pants: no-infer-dep
from a2a.server.request_handlers import DefaultRequestHandler  # pants: no-infer-dep
from a2a.server.tasks import InMemoryTaskStore  # pants: no-infer-dep
from next_gen_ui_a2a.agent_card import card  # type: ignore[import-not-found]
from next_gen_ui_a2a.agent_executor import NextGenUIAgentExecutor  # type: ignore[import-not-found]
from langchain_openai import ChatOpenAI  # pants: no-infer-dep
from next_gen_ui_agent.model import LangChainModelInference
from next_gen_ui_agent.types import AgentConfig

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "ollama"
    model = os.getenv("INFERENCE_MODEL", "llama3.2")
    base_url = os.getenv("OPEN_API_URL", "http://localhost:11434/v1")

    logger.info(
        "Starting Next Gen UI A2A Server. base_url=%s, model=%s", base_url, model
    )

    llm = ChatOpenAI(model=model, base_url=base_url)
    inference = LangChainModelInference(llm)
    config = AgentConfig(inference=inference)

    request_handler = DefaultRequestHandler(
        agent_executor=NextGenUIAgentExecutor(config),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=9999)

"""NGUI agent setup for LlamaStack."""

from app.config import NGUI_CONFIG, NGUI_MODEL
from app.llm import get_llm_client
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent

# Singleton agent instance
_ngui_agent_instance = None


async def get_ngui_agent():
    """Get or create the NGUI agent."""
    global _ngui_agent_instance
    if _ngui_agent_instance is None:
        client = get_llm_client()
        _ngui_agent_instance = NextGenUILlamaStackAgent(
            client, NGUI_MODEL, config=NGUI_CONFIG
        )
    return _ngui_agent_instance

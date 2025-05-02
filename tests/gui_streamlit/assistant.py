import json
import logging

from langchain_core.language_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage, ChatMessage, ToolMessage
from langgraph.graph.graph import CompiledGraph
from next_gen_ui_agent.renderer.base_renderer import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent
from next_gen_ui_patternfly_renderer.patternfly_renderer import (
    PatternflyStrategyFactory,
)
from next_gen_ui_rhds_renderer.rhds_renderer import RhdsStrategyFactory
from stevedore.extension import Extension, ExtensionManager

logger = logging.getLogger(__name__)


def create_ngui_graph(llm_data: list[str | dict]):
    msg = AIMessage(content=json.dumps(llm_data, default=str))
    ngui_model = FakeMessagesListChatModel(responses=[msg], cache=False)
    ngui_graph = NextGenUILangGraphAgent(ngui_model)
    extension_rhds = Extension(
        name="rhds", entry_point=None, plugin=None, obj=RhdsStrategyFactory()
    )
    extension_patternfly = Extension(
        name="patternfly",
        entry_point=None,
        plugin=None,
        obj=PatternflyStrategyFactory(),
    )
    em = ExtensionManager(PLUGGABLE_RENDERERS_NAMESPACE).make_test_instance(
        extensions=[extension_rhds, extension_patternfly],
        namespace=PLUGGABLE_RENDERERS_NAMESPACE,
    )
    ngui_graph.ngui_agent._extension_manager = em
    return ngui_graph


async def call_assistant(
    assistant: CompiledGraph,
    messages: list[BaseMessage],
    component_system: str,
) -> str:
    logger.debug("Sending mesages to the NGUI Agent.count=%s", len(messages))

    async for msg, metadata in assistant.astream(
        {"messages": messages},
        {"configurable": {"component_system": component_system}},
        stream_mode="messages",
    ):
        langgraph_node = metadata["langgraph_node"]  # type: ignore
        if langgraph_node == "design_system_handler" and msg.content:  # type: ignore
            return msg.content  # type: ignore
    return ""


async def execute_ngui_agent(
    llm_data: list[str | dict],
    prompt: str,
    input_data: str,
    component_system: str,
) -> str:
    ngui_graph = create_ngui_graph(llm_data)
    assistant = ngui_graph.build_graph()
    logger.info(prompt)
    logger.info(input_data)

    messages: list[BaseMessage] = []
    messages.append(ChatMessage(content=prompt, role="user"))
    messages.append(ToolMessage(content=input_data, tool_call_id="test-id"))
    msg_content = await call_assistant(assistant, messages, component_system)

    return msg_content

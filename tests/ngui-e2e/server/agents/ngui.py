"""NGUI agent setup with different strategies."""
from next_gen_ui_agent.agent_config import AgentConfig
from next_gen_ui_agent.types import AgentConfigDataType
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent

from llm import llm

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


"""NGUI agent setup with different strategies."""

import logging

from config import SHARED_DATA_TYPES
from data_sources.data_loader import get_namespaces_data, get_nodes_data, get_pods_data
from data_sources.mock_mcp_server import MockOpenShiftMCPServer
from langgraph.prebuilt import create_react_agent
from llm import llm
from next_gen_ui_agent import AgentConfig
from next_gen_ui_langgraph.agent import NextGenUILangGraphAgent

# Initialize mock MCP server with sample data
_openshift_mcp_server = MockOpenShiftMCPServer(
    pods_data=get_pods_data(),
    nodes_data=get_nodes_data(),
    namespaces_data=get_namespaces_data(),
)

# Get LangChain tools from the mock MCP server
_openshift_tools = _openshift_mcp_server.get_langchain_tools()

# Debug: Verify tools are loaded
logger = logging.getLogger(__name__)
tool_names = [tool.name for tool in _openshift_tools]
logger.info("Loaded OpenShift tools: %s", tool_names)

# Create a LangGraph agent with OpenShift tools
# This agent can fetch OpenShift data using the tools
_openshift_agent = create_react_agent(
    model=llm,
    tools=_openshift_tools,
    prompt="""You are a helpful OpenShift cluster assistant. You MUST use the available tools to answer user questions about pods, nodes, and namespaces.

CRITICAL: You MUST call a tool for every user query. Do not provide answers without calling a tool first.

TOOL SELECTION:
- For pod queries (including "show pods", "list pods", "get pods") → use get_openshift_pods() or get_openshift_pod_details()
- For node queries (including "show nodes", "list nodes", "get nodes") → use get_openshift_nodes() or get_openshift_node_details()
- For namespace queries (including "show namespaces", "list namespaces", "get namespaces") → use get_openshift_namespaces()

FILTERING:
- get_openshift_pods supports: pod_name, namespace, status (Running, Pending, Error, Failed)
- get_openshift_nodes supports: node_name
- get_openshift_namespaces supports: namespace_name, project

EXAMPLES:
- "show me namespaces" → call get_openshift_namespaces()
- "get openshift namespaces" → call get_openshift_namespaces()
- "list all namespaces" → call get_openshift_namespaces()
- "show pods" → call get_openshift_pods()
- "get nodes" → call get_openshift_nodes()

When the user asks about OpenShift resources, you MUST call the appropriate tool to fetch the data.
Always return the full JSON response from the tool so the downstream system can process it.""",
)

# One-step strategy agent (for UI generation)
config_onestep = AgentConfig(
    component_selection_strategy="one_llm_call", data_types=SHARED_DATA_TYPES
)
ngui_agent_onestep_instance = NextGenUILangGraphAgent(model=llm, config=config_onestep)
ngui_agent_onestep = ngui_agent_onestep_instance.build_graph()

# Two-step strategy agent (for UI generation)
config_twostep = AgentConfig(
    component_selection_strategy="two_llm_calls", data_types=SHARED_DATA_TYPES
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

# Export the OpenShift agent and tools for use in routes
openshift_agent = _openshift_agent
openshift_tools = _openshift_tools
openshift_mcp_server = _openshift_mcp_server

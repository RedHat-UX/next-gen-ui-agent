import asyncio
import json
import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from next_gen_ui_langgraph import NextGenUILangGraphAgent

# Import comprehensive K8s data from data_set_k8s
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from next_gen_ui_testing.data_set_k8s import (
    find_cluster,
    openshift_clusters,
    find_cluster_nodes,
    find_pod_issues,
    find_cost_analysis,
)

if not os.environ.get("OPENAI_API_KEY"):
    # getpass.getpass("Enter your OpenAI API key: ")
    os.environ["OPENAI_API_KEY"] = "ollama"

llm = ChatOpenAI(model="llama3.2", base_url="http://localhost:11434/v1")


# K8s Agent
# Get cluster tool
def get_cluster(cluster_name: str):
    """Call to get OpenShift cluster information.
    Args:
    cluster_name: Cluster name e.g. 'Production' or 'Development'
    """
    print(f"Searching for cluster: '{cluster_name}'")
    result = find_cluster(cluster_name)
    if result:
        print(f"Returning JSON payload for cluster")
        return json.dumps(result, default=str)
    print(f"Cluster '{cluster_name}' not found")
    return None


k8s_agent = create_react_agent(
    model=llm,
    tools=[get_cluster],
    prompt="You are a helpful OpenShift/Kubernetes assistant that provides cluster information, health status, and resource usage details",
)

# Next Gen UI Agent - Build it as Standard LangGraph agent
ngui_agent = NextGenUILangGraphAgent(model=llm).build_graph()
component_system = "json"
# component_system = "rhds" # use rhds if you have installed package next_gen_ui_rhds_renderer
ngui_cfg = {"configurable": {"component_system": component_system}}


def run() -> None:
    # Run K8s Agent to get raw cluster data and answer
    prompt = "Show me details of production OpenShift cluster"
    # prompt = "Show me the development cluster status"
    # prompt = "What is the health status of prod-openshift-us-east?"
    # prompt = "How many nodes does the production cluster have?"
    # prompt = "Show me CPU and memory usage of production cluster"
    k8s_response = k8s_agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]}
    )
    print("\n\n===K8s Text Answer===\n", k8s_response["messages"][-1].content)

    # Run NGUI Agent to get UI component as JSON for client-side rendering
    ngui_response = asyncio.run(
        # Run Next Gen UI Agent. Pass k8s agent response directly.
        ngui_agent.ainvoke(k8s_response, ngui_cfg),
    )

    print(
        f"\n\n===Next Gen UI {component_system} Rendition===\n",
        ngui_response["renditions"][0].content,
    )


if __name__ == "__main__":
    run()


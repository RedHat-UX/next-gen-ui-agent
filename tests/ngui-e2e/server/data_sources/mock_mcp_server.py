"""Mock MCP server for OpenShift tools.

This module provides a mock MCP server that serves up OpenShift-related tools
like get_openshift_pods and get_openshift_nodes. This makes the tool calls more
modular and reusable compared to the inline data simulation approach.

The server can be used in two ways:
1. As an MCP server (via FastMCP) for MCP clients
2. As LangChain tools (via get_langchain_tools()) for LangGraph integration

Example usage:
    # Initialize with data
    pods_data = [{"name": "pod-1", "status": "Running", ...}, ...]
    nodes_data = [{"name": "node-1", "status": "Ready", ...}, ...]
    server = MockOpenShiftMCPServer(pods_data, nodes_data)

    # Use with LangGraph
    tools = server.get_langchain_tools()
    agent = create_react_agent(model=llm, tools=tools)

    # Or use as MCP server
    mcp_instance = server.get_mcp_instance()
"""

import json
import re
from typing import Annotated, Optional

from fastmcp import FastMCP
from langchain_core.tools import tool
from pydantic import Field
from utils.logging import log_info


def _extract_pod_name(prompt: str) -> Optional[str]:
    """Extract pod name from prompt using multiple patterns."""
    prompt_lower = prompt.lower()
    pod_name_match = re.search(r"\bpod(?:s)?\s+([a-zA-Z0-9-]+)", prompt_lower)
    if pod_name_match:
        return pod_name_match.group(1)
    pod_name_match = re.search(
        r"(?:about|details|for)\s+pod\s+([a-zA-Z0-9-]+)", prompt_lower
    )
    if pod_name_match:
        return pod_name_match.group(1)
    pod_name_match = re.search(
        r"pod\s+(?:named|called)\s+([a-zA-Z0-9-]+)", prompt_lower
    )
    if pod_name_match:
        return pod_name_match.group(1)
    return None


def _extract_namespace(prompt: str) -> Optional[str]:
    """Extract namespace from prompt."""
    prompt_lower = prompt.lower()
    ns_match = re.search(r"namespace\s+([a-zA-Z0-9-]+)", prompt_lower)
    if ns_match:
        namespace = ns_match.group(1)
        if namespace != "namespace":
            return namespace
    ns_match = re.search(r"\bin\s+([a-zA-Z0-9-]+)", prompt_lower)
    if ns_match:
        namespace = ns_match.group(1)
        if namespace not in ["namespace", "the", "a", "an"]:
            return namespace
    return None


def _extract_node_name(prompt: str) -> Optional[str]:
    """Extract node name from prompt using multiple patterns."""
    prompt_lower = prompt.lower()
    node_name_match = re.search(r"\bnode(?:s)?\s+([a-zA-Z0-9-]+)", prompt_lower)
    if node_name_match:
        return node_name_match.group(1)
    node_name_match = re.search(
        r"(?:about|details|for)\s+node\s+([a-zA-Z0-9-]+)", prompt_lower
    )
    if node_name_match:
        return node_name_match.group(1)
    return None


def _extract_namespace_name(prompt: str) -> Optional[str]:
    """Extract namespace name from prompt using multiple patterns."""
    prompt_lower = prompt.lower()
    # Pattern 1: "namespace {name}" or "namespaces {name}"
    ns_match = re.search(r"\bnamespace(?:s)?\s+([a-zA-Z0-9-]+)", prompt_lower)
    if ns_match:
        namespace = ns_match.group(1)
        if namespace != "namespace" and namespace != "namespaces":
            return namespace
    # Pattern 2: "in namespace {name}"
    ns_match = re.search(r"\bin\s+namespace\s+([a-zA-Z0-9-]+)", prompt_lower)
    if ns_match:
        return ns_match.group(1)
    return None


def _filter_namespaces(
    namespaces: list[dict],
    namespace_name: Optional[str] = None,
    project: Optional[str] = None,
) -> list[dict]:
    """Filter namespaces based on provided criteria."""
    filtered = namespaces
    if namespace_name:
        filtered = [
            ns
            for ns in filtered
            if str(ns.get("name", "")).lower() == namespace_name.lower()
        ]
    if project:
        filtered = [
            ns
            for ns in filtered
            if str(ns.get("project", "")).lower() == project.lower()
        ]
    return filtered


def _filter_pods(
    pods: list[dict],
    pod_name: Optional[str] = None,
    namespace: Optional[str] = None,
    status: Optional[str] = None,
) -> list[dict]:
    """Filter pods based on provided criteria."""
    filtered = pods
    if pod_name:
        filtered = [
            p for p in filtered if str(p.get("name", "")).lower() == pod_name.lower()
        ]
    if namespace:
        filtered = [
            p
            for p in filtered
            if str(p.get("namespace", "")).lower() == namespace.lower()
        ]
    if status:
        if status == "error":
            filtered = [
                p
                for p in filtered
                if str(p.get("status", "")).lower()
                in ["error", "failed", "crashloopbackoff"]
            ]
        else:
            filtered = [
                p
                for p in filtered
                if str(p.get("status", "")).lower() == status.lower()
            ]
    return filtered


def _filter_nodes(nodes: list[dict], node_name: Optional[str] = None) -> list[dict]:
    """Filter nodes based on provided criteria."""
    filtered = nodes
    if node_name:
        filtered = [
            n for n in filtered if str(n.get("name", "")).lower() == node_name.lower()
        ]
    return filtered


class MockOpenShiftMCPServer:
    """Mock MCP server for OpenShift tools."""

    def __init__(
        self,
        pods_data: list[dict],
        nodes_data: list[dict],
        namespaces_data: Optional[list[dict]] = None,
    ):
        """Initialize the mock MCP server with data.

        Args:
            pods_data: List of pod dictionaries
            nodes_data: List of node dictionaries
            namespaces_data: Optional list of namespace dictionaries
        """
        self.pods_data = pods_data
        self.nodes_data = nodes_data
        self.namespaces_data = namespaces_data or []
        # Initialize FastMCP with just the name
        # Note: We're primarily using LangChain tools, so MCP server functionality is optional
        self.mcp = FastMCP("MockOpenShiftMCPServer")
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up MCP tools for OpenShift resources."""

        @self.mcp.tool(
            name="get_openshift_pods",
            description=(
                "Get OpenShift pods. Supports filtering by pod name, namespace, and status. "
                "Returns a JSON string containing a 'pods' array with pod information."
            ),
        )
        async def get_openshift_pods(
            pod_name: Annotated[
                Optional[str],
                Field(description="Optional pod name to filter by (case-insensitive)"),
            ] = None,
            namespace: Annotated[
                Optional[str],
                Field(description="Optional namespace to filter by (case-insensitive)"),
            ] = None,
            status: Annotated[
                Optional[str],
                Field(
                    description="Optional status to filter by: 'Running', 'Pending', 'Error', 'Failed'"
                ),
            ] = None,
        ) -> str:
            """Get OpenShift pods with optional filtering."""
            log_info(
                f"get_openshift_pods called with pod_name={pod_name}, namespace={namespace}, status={status}"
            )
            filtered_pods = _filter_pods(self.pods_data, pod_name, namespace, status)
            result = {"pods": filtered_pods}
            return json.dumps(result)

        @self.mcp.tool(
            name="get_openshift_pod_details",
            description=(
                "Get detailed information about a specific OpenShift pod. "
                "Requires pod_name. Optionally filters by namespace. "
                "Returns detailed pod information including containers, events, and labels."
            ),
        )
        async def get_openshift_pod_details(
            pod_name: Annotated[
                str,
                Field(description="Pod name to get details for (required)"),
            ],
            namespace: Annotated[
                Optional[str],
                Field(description="Optional namespace to filter by"),
            ] = None,
        ) -> str:
            """Get detailed information about a specific pod."""
            log_info(
                f"get_openshift_pod_details called with pod_name={pod_name}, namespace={namespace}"
            )
            matching_pods = _filter_pods(self.pods_data, pod_name, namespace)

            if not matching_pods:
                return json.dumps({"pod": None, "pods": self.pods_data})

            pod = matching_pods[0]
            # Create detailed pod information
            detailed_pod = {
                "name": pod.get("name"),
                "namespace": pod.get("namespace"),
                "status": pod.get("status"),
                "created": pod.get("created"),
                "cpu_usage": pod.get("cpu_usage"),
                "memory_usage": pod.get("memory_usage"),
                "image": f"{pod.get('namespace', 'default')}/{pod.get('name', 'unknown')}:latest",
                "restart_count": 3 if pod.get("status") == "Error" else 0,
                "node_name": (
                    "worker-0" if pod.get("namespace") == "default" else "worker-1"
                ),
                "labels": {
                    "app": (
                        pod.get("name", "").split("-")[0]
                        if "-" in pod.get("name", "")
                        else "app"
                    ),
                    "version": "v1.0.0",
                },
                "containers": [
                    {
                        "name": pod.get("name", "").replace("pod-", "container-"),
                        "image": f"{pod.get('namespace', 'default')}/{pod.get('name', 'unknown')}:latest",
                        "ready": pod.get("status") == "Running",
                        "restarts": 3 if pod.get("status") == "Error" else 0,
                    }
                ],
                "events": (
                    [
                        {
                            "type": "Normal",
                            "reason": "Started",
                            "message": "Container started successfully",
                            "timestamp": pod.get("created"),
                        }
                    ]
                    if pod.get("status") == "Running"
                    else [
                        {
                            "type": "Warning",
                            "reason": "Failed",
                            "message": "Container failed to start",
                            "timestamp": pod.get("created"),
                        }
                    ]
                ),
            }
            result = {"pod": detailed_pod, "pods": self.pods_data}
            return json.dumps(result)

        @self.mcp.tool(
            name="get_openshift_nodes",
            description=(
                "Get OpenShift nodes. Supports filtering by node name. "
                "Returns a JSON string containing a 'nodes' array with node information."
            ),
        )
        async def get_openshift_nodes(
            node_name: Annotated[
                Optional[str],
                Field(description="Optional node name to filter by (case-insensitive)"),
            ] = None,
        ) -> str:
            """Get OpenShift nodes with optional filtering."""
            log_info(f"get_openshift_nodes called with node_name={node_name}")
            filtered_nodes = _filter_nodes(self.nodes_data, node_name)
            result = {"nodes": filtered_nodes}
            return json.dumps(result)

        @self.mcp.tool(
            name="get_openshift_node_details",
            description=(
                "Get detailed information about a specific OpenShift node. "
                "Requires node_name. Returns detailed node information."
            ),
        )
        async def get_openshift_node_details(
            node_name: Annotated[
                str,
                Field(description="Node name to get details for (required)"),
            ],
        ) -> str:
            """Get detailed information about a specific node."""
            log_info(f"get_openshift_node_details called with node_name={node_name}")
            matching_nodes = _filter_nodes(self.nodes_data, node_name)

            if not matching_nodes:
                return json.dumps({"node": None, "nodes": self.nodes_data})

            node = matching_nodes[0]
            # Create detailed node information
            detailed_node = {
                "name": node.get("name"),
                "status": node.get("status"),
                "created": node.get("created"),
                "cpu": node.get("cpu"),
                "memory": node.get("memory"),
                "version": node.get("version"),
                "region": node.get("region"),
                "pods": [
                    {
                        "name": f"pod-on-{node.get('name', 'unknown')}",
                        "namespace": "default",
                    }
                ],
                "conditions": [
                    {
                        "type": "Ready",
                        "status": "True" if node.get("status") == "Ready" else "False",
                    }
                ],
            }
            result = {"node": detailed_node, "nodes": self.nodes_data}
            return json.dumps(result)

        @self.mcp.tool(
            name="get_openshift_namespaces",
            description=(
                "Get OpenShift namespaces. Supports filtering by namespace name and project. "
                "Returns a JSON string containing a 'namespaces' array with namespace information."
            ),
        )
        async def get_openshift_namespaces(
            namespace_name: Annotated[
                Optional[str],
                Field(
                    description="Optional namespace name to filter by (case-insensitive)"
                ),
            ] = None,
            project: Annotated[
                Optional[str],
                Field(
                    description="Optional project name to filter by (case-insensitive)"
                ),
            ] = None,
        ) -> str:
            """Get OpenShift namespaces with optional filtering."""
            log_info(
                f"get_openshift_namespaces called with namespace_name={namespace_name}, project={project}"
            )
            filtered_namespaces = _filter_namespaces(
                self.namespaces_data, namespace_name, project
            )
            result = {"namespaces": filtered_namespaces}
            return json.dumps(result)

    def get_langchain_tools(self) -> list:
        """Get LangChain-compatible tools for use with LangGraph.

        Returns:
            List of LangChain tool functions that can be used with create_react_agent.
        """
        # Create synchronous wrappers for the async MCP tools
        pods_data = self.pods_data
        nodes_data = self.nodes_data
        namespaces_data = self.namespaces_data

        @tool
        def get_openshift_pods(
            pod_name: Optional[str] = None,
            namespace: Optional[str] = None,
            status: Optional[str] = None,
        ) -> str:
            """Get OpenShift pods. Supports filtering by pod name, namespace, and status.

            Args:
                pod_name: Optional pod name to filter by (case-insensitive)
                namespace: Optional namespace to filter by (case-insensitive)
                status: Optional status to filter by: 'Running', 'Pending', 'Error', 'Failed'

            Returns:
                JSON string containing a 'pods' array with pod information.
            """
            filtered_pods = _filter_pods(pods_data, pod_name, namespace, status)
            result = {"pods": filtered_pods}
            return json.dumps(result)

        @tool
        def get_openshift_pod_details(
            pod_name: str, namespace: Optional[str] = None
        ) -> str:
            """Get detailed information about a specific OpenShift pod.

            Args:
                pod_name: Pod name to get details for (required)
                namespace: Optional namespace to filter by

            Returns:
                JSON string containing detailed pod information.
            """
            matching_pods = _filter_pods(pods_data, pod_name, namespace)

            if not matching_pods:
                return json.dumps({"pod": None, "pods": pods_data})

            pod = matching_pods[0]
            detailed_pod = {
                "name": pod.get("name"),
                "namespace": pod.get("namespace"),
                "status": pod.get("status"),
                "created": pod.get("created"),
                "cpu_usage": pod.get("cpu_usage"),
                "memory_usage": pod.get("memory_usage"),
                "image": f"{pod.get('namespace', 'default')}/{pod.get('name', 'unknown')}:latest",
                "restart_count": 3 if pod.get("status") == "Error" else 0,
                "node_name": (
                    "worker-0" if pod.get("namespace") == "default" else "worker-1"
                ),
                "labels": {
                    "app": (
                        pod.get("name", "").split("-")[0]
                        if "-" in pod.get("name", "")
                        else "app"
                    ),
                    "version": "v1.0.0",
                },
                "containers": [
                    {
                        "name": pod.get("name", "").replace("pod-", "container-"),
                        "image": f"{pod.get('namespace', 'default')}/{pod.get('name', 'unknown')}:latest",
                        "ready": pod.get("status") == "Running",
                        "restarts": 3 if pod.get("status") == "Error" else 0,
                    }
                ],
                "events": (
                    [
                        {
                            "type": "Normal",
                            "reason": "Started",
                            "message": "Container started successfully",
                            "timestamp": pod.get("created"),
                        }
                    ]
                    if pod.get("status") == "Running"
                    else [
                        {
                            "type": "Warning",
                            "reason": "Failed",
                            "message": "Container failed to start",
                            "timestamp": pod.get("created"),
                        }
                    ]
                ),
            }
            result = {"pod": detailed_pod, "pods": pods_data}
            return json.dumps(result)

        @tool
        def get_openshift_nodes(node_name: Optional[str] = None) -> str:
            """Get OpenShift nodes. Supports filtering by node name.

            Args:
                node_name: Optional node name to filter by (case-insensitive)

            Returns:
                JSON string containing a 'nodes' array with node information.
            """
            filtered_nodes = _filter_nodes(nodes_data, node_name)
            result = {"nodes": filtered_nodes}
            return json.dumps(result)

        @tool
        def get_openshift_node_details(node_name: str) -> str:
            """Get detailed information about a specific OpenShift node.

            Args:
                node_name: Node name to get details for (required)

            Returns:
                JSON string containing detailed node information.
            """
            matching_nodes = _filter_nodes(nodes_data, node_name)

            if not matching_nodes:
                return json.dumps({"node": None, "nodes": nodes_data})

            node = matching_nodes[0]
            detailed_node = {
                "name": node.get("name"),
                "status": node.get("status"),
                "created": node.get("created"),
                "cpu": node.get("cpu"),
                "memory": node.get("memory"),
                "version": node.get("version"),
                "region": node.get("region"),
                "pods": [
                    {
                        "name": f"pod-on-{node.get('name', 'unknown')}",
                        "namespace": "default",
                    }
                ],
                "conditions": [
                    {
                        "type": "Ready",
                        "status": "True" if node.get("status") == "Ready" else "False",
                    }
                ],
            }
            result = {"node": detailed_node, "nodes": nodes_data}
            return json.dumps(result)

        @tool
        def get_openshift_namespaces(
            namespace_name: Optional[str] = None, project: Optional[str] = None
        ) -> str:
            """Get OpenShift namespaces. Supports filtering by namespace name and project.

            Args:
                namespace_name: Optional namespace name to filter by (case-insensitive)
                project: Optional project name to filter by (case-insensitive)

            Returns:
                JSON string containing a 'namespaces' array with namespace information.
            """
            filtered_namespaces = _filter_namespaces(
                namespaces_data, namespace_name, project
            )
            result = {"namespaces": filtered_namespaces}
            return json.dumps(result)

        return [
            get_openshift_pods,
            get_openshift_pod_details,
            get_openshift_nodes,
            get_openshift_node_details,
            get_openshift_namespaces,
        ]

    def get_mcp_instance(self) -> FastMCP:
        """Get the underlying FastMCP instance.

        Returns:
            The FastMCP instance for direct use.
        """
        return self.mcp

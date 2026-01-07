from typing import Optional

from next_gen_ui_agent.types import AgentConfig
from pydantic import BaseModel, Field


class MCPAgentToolConfig(BaseModel):
    """Information to override default values in the MCP Agent tool."""

    description: Optional[str] = Field(
        description="Description of the MCP tool.",
        default=None,
    )
    """Description of the MCP tool."""

    argument_descriptions: Optional[dict[str, str]] = Field(
        description="Dictionary mapping argument names to their descriptions. Overrides default argument descriptions.",
        default=None,
    )
    """Dictionary mapping argument names to their descriptions. Overrides default argument descriptions."""


class MCPAgentToolsConfig(BaseModel):
    """Tools info to override default values in the MCP Agent."""

    generate_ui_component: Optional[MCPAgentToolConfig] = Field(
        default=None,
        description="`generate_ui_components` tool info to override default values in the MCP Agent.",
    )
    """`generate_ui_components` tool info to override default values in the MCP Agent."""

    generate_ui_multiple_components: Optional[MCPAgentToolConfig] = Field(
        default=None,
        description="`generate_ui_multiple_components` tool info to override default values in the MCP Agent.",
    )
    """`generate_ui_multiple_components` tool info to override default values in the MCP Agent."""


class MCPConfig(BaseModel):

    tools: Optional[MCPAgentToolsConfig] = Field(
        default=None,
        description="Tools info to override default values in the MCP Agent.",
    )
    """Tools info to override default values in the MCP Agent."""


class MCPAgentConfig(AgentConfig):
    """MCP Agent Configuration."""

    mcp: Optional[MCPConfig] = Field(
        default=None,
        description="MCP related configuration.",
    )
    """MCP related configuration."""

from typing import List, Optional

from next_gen_ui_agent.types import AgentConfig
from pydantic import BaseModel, Field


class MCPAgentToolConfig(BaseModel):
    """Information to override default values in the MCP Agent tool."""

    enabled: Optional[bool] = Field(
        description="Whether the tool is enabled. Defaults to True. If False, the tool will not be exposed from the MCP server to client.",
        default=True,
    )
    """Whether the tool is enabled. Defaults to True."""

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

    schema_excluded_args: Optional[List[str]] = Field(
        description="List of argument names to exclude from the MCP tool schema, so calling LLM does not see them. They can be send still to the MCP server. 'session_id' is always excluded by default. Additional arguments listed here will be added to the exclusion list.",
        default=None,
    )
    """List of argument names to exclude from the MCP tool schema. 'session_id' is always excluded by default."""


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

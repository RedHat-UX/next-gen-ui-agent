from typing import Optional

from next_gen_ui_agent.types import AgentConfig
from pydantic import BaseModel, Field


class A2AAgentCardInfo(BaseModel):
    """Information to override default values in the A2A Agent card."""

    name: Optional[str] = Field(
        description="Name of the A2A Agent.",
        default=None,
    )
    """Name of the A2A Agent."""
    description: Optional[str] = Field(
        description="Description of the A2A Agent.",
        default=None,
    )
    """Description of the A2A Agent."""
    url: Optional[str] = Field(
        description="URL of the A2A Agent. Use if you want to override the real URL of the A2A Agent, eg. when running behind a proxy or load balancer.",
        default=None,
    )
    """URL of the A2A Agent. Use if you want to override the real URL of the A2A Agent, eg. when running behind a proxy or load balancer."""


class A2AAgentSkill(BaseModel):
    """Information to override default values in the A2A Agent skill."""

    name: Optional[str] = Field(
        default=None,
        description="Name of the A2A Agent skill.",
    )
    """Name of the A2A Agent skill."""
    description: Optional[str] = Field(
        default=None,
        description="Description of the A2A Agent skill.",
    )
    """Description of the A2A Agent skill."""
    tags: Optional[list[str]] = Field(
        default=None,
        description="Tags of the A2A Agent skill.",
    )
    """Tags of the A2A Agent skill."""
    examples: Optional[list[str]] = Field(
        default=None,
        description="Examples of the A2A Agent skill.",
    )
    """Examples of the A2A Agent skill."""


class A2AAgentSkills(BaseModel):
    """Skills info to override default values in the A2A Agent card."""

    generate_ui_components: Optional[A2AAgentSkill] = Field(
        default=None,
        description="`generate_ui_components` skill info to override default values in the A2A Agent card.",
    )
    """`generate_ui_components` skill info to override default values in the A2A Agent card."""


class A2AConfig(BaseModel):

    agent_card: Optional[A2AAgentCardInfo] = Field(
        default=None,
        description="Information to override default values in the A2A Agent card.",
    )
    """Information to override default values in the A2A Agent card."""

    skills: Optional[A2AAgentSkills] = Field(
        default=None,
        description="Skills info to override default values in the A2A Agent card.",
    )
    """Skills info to override default values in the A2A Agent card."""


class A2AAgentConfig(AgentConfig):
    """A2A Agent Configuration."""

    a2a: Optional[A2AConfig] = Field(
        default=None,
        description="A2A related configuration.",
    )
    """A2A related configuration."""

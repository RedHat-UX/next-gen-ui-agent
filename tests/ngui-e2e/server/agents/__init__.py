"""Agent initialization and setup."""

from .movies import movies_agent
from .ngui import ngui_agents, openshift_agent

__all__ = ["movies_agent", "ngui_agents", "openshift_agent"]

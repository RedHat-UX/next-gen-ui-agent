import os
from importlib.metadata import version as get_package_version

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from next_gen_ui_a2a.agent_config import A2AAgentConfig

# Default values
DEFAULT_PACKAGE_VERSION = "1.0.0"
SKILL_ID_GENERATE_UI_COMPONENTS = "generate_ui_components"
DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME = "Generate UI components"
DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION = "Generates the best UI components for the user's prompt and the structure and values of the individual strucutred input data pieces."
DEFAULT_SKILL_GENERATE_UI_COMPONENTS_TAGS = [
    "ui",
    "data visualization",
    "ux",
    "frontend",
    "user interface",
    "ui generation",
    "structured data",
]
DEFAULT_SKILL_GENERATE_UI_COMPONENTS_EXAMPLES = [
    "First message TextPart should be user prompt. Structured input data could be passed as 'data' field in metadata or following DataParts"
]


def _get_package_version() -> str:
    """Get the version of next_gen_ui_a2a package."""

    env_version = os.environ.get("NGUI_A2A_VERSION")
    if env_version and env_version.strip() != "":
        return env_version

    try:
        return get_package_version("next_gen_ui_a2a")
    except Exception:
        return DEFAULT_PACKAGE_VERSION


def _get_skill_generate_ui_components(agent_config: A2AAgentConfig) -> AgentSkill:
    """Get skill definition for generating UI components."""

    skill_info = (
        agent_config.a2a.skills.generate_ui_components
        if agent_config.a2a
        and agent_config.a2a.skills
        and agent_config.a2a.skills.generate_ui_components
        else None
    )

    return AgentSkill(
        id=SKILL_ID_GENERATE_UI_COMPONENTS,
        name=(
            skill_info.name
            if skill_info and skill_info.name
            else DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME
        ),
        description=(
            skill_info.description
            if skill_info and skill_info.description
            else DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION
        ),
        tags=(
            skill_info.tags
            if skill_info and skill_info.tags
            else DEFAULT_SKILL_GENERATE_UI_COMPONENTS_TAGS
        ),
        examples=(
            skill_info.examples
            if skill_info and skill_info.examples
            else DEFAULT_SKILL_GENERATE_UI_COMPONENTS_EXAMPLES
        ),
    )


DEFAULT_AGENT_CARD_NAME = "Next Gen UI Agent"
DEFAULT_AGENT_CARD_DESCRIPTION = "Generates UI component to visualize structured input data to the user, regarding the user's prompt and input data structure and values."


def create_agent_card(agent_config: A2AAgentConfig, real_url: str) -> AgentCard:
    """Create A2A agent card for Next Gen UI Agent"""

    agent_card_info = (
        agent_config.a2a.agent_card
        if agent_config.a2a and agent_config.a2a.agent_card
        else None
    )

    return AgentCard(
        name=(
            agent_card_info.name
            if agent_card_info and agent_card_info.name
            else DEFAULT_AGENT_CARD_NAME
        ),
        description=(
            agent_card_info.description
            if agent_card_info and agent_card_info.description
            else DEFAULT_AGENT_CARD_DESCRIPTION
        ),
        url=(
            agent_card_info.url if agent_card_info and agent_card_info.url else real_url
        ),
        version=_get_package_version(),
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[_get_skill_generate_ui_components(agent_config)],
        supports_authenticated_extended_card=False,
    )

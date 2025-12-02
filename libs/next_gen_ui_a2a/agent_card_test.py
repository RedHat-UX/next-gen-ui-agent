import os
from unittest.mock import Mock, patch

from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from next_gen_ui_a2a.agent_card import (
    DEFAULT_AGENT_CARD_DESCRIPTION,
    DEFAULT_AGENT_CARD_NAME,
    DEFAULT_PACKAGE_VERSION,
    DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION,
    DEFAULT_SKILL_GENERATE_UI_COMPONENTS_EXAMPLES,
    DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME,
    DEFAULT_SKILL_GENERATE_UI_COMPONENTS_TAGS,
    SKILL_ID_GENERATE_UI_COMPONENTS,
    _get_package_version,
    _get_skill_generate_ui_components,
    create_agent_card,
)
from next_gen_ui_a2a.agent_config import (
    A2AAgentCardInfo,
    A2AAgentConfig,
    A2AAgentSkill,
    A2AAgentSkills,
    A2AConfig,
)


class TestGetPackageVersion:
    """Tests for _get_package_version function."""

    def test_get_package_version_when_installed(self) -> None:
        """Test that version is retrieved when package is installed."""
        with patch("next_gen_ui_a2a.agent_card.get_package_version") as mock_version:
            mock_version.return_value = "2.3.4"
            result = _get_package_version()
            assert result == "2.3.4"
            mock_version.assert_called_once_with("next_gen_ui_a2a")

    def test_get_package_version_fallback_to_env_var(self) -> None:
        """Test that version falls back to environment variable when package is not installed."""
        with patch("next_gen_ui_a2a.agent_card.get_package_version") as mock_version:
            mock_version.side_effect = Exception("Package not found")
            with patch.dict(os.environ, {"VERSION": "3.0.0"}):
                result = _get_package_version()
                assert result == "3.0.0"

    def test_get_package_version_fallback_to_default(self) -> None:
        """Test that version falls back to default when package is not installed and no env var."""
        with patch("next_gen_ui_a2a.agent_card.get_package_version") as mock_version:
            mock_version.side_effect = Exception("Package not found")
            with patch.dict(os.environ, {}, clear=True):
                result = _get_package_version()
                assert result == DEFAULT_PACKAGE_VERSION


class TestGetSkillGenerateUIComponents:
    """Tests for _get_skill_generate_ui_components function."""

    def test_get_skill_with_defaults(self) -> None:
        """Test that skill uses default values when no config is provided."""
        config = A2AAgentConfig()
        skill = _get_skill_generate_ui_components(config)

        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME
        assert skill.description == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION
        assert skill.tags == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_TAGS
        assert skill.examples == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_EXAMPLES

    def test_get_skill_with_full_config(self) -> None:
        """Test that skill uses all provided config values."""
        skill_info = A2AAgentSkill(
            name="Custom UI Generator",
            description="Custom description for UI generation",
            tags=["custom", "ui", "generation"],
            examples=["Example 1", "Example 2"],
        )
        config = A2AAgentConfig(
            a2a=A2AConfig(skills=A2AAgentSkills(generate_ui_components=skill_info))
        )
        skill = _get_skill_generate_ui_components(config)

        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == "Custom UI Generator"
        assert skill.description == "Custom description for UI generation"
        assert skill.tags == ["custom", "ui", "generation"]
        assert skill.examples == ["Example 1", "Example 2"]

    def test_get_skill_with_partial_config(self) -> None:
        """Test that skill uses provided values and defaults for missing ones."""
        skill_info = A2AAgentSkill(
            name="Partial Config Skill",
            description=None,  # Should use default
            tags=None,  # Should use default
            examples=["Custom example"],
        )
        config = A2AAgentConfig(
            a2a=A2AConfig(skills=A2AAgentSkills(generate_ui_components=skill_info))
        )
        skill = _get_skill_generate_ui_components(config)

        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == "Partial Config Skill"
        assert (
            skill.description == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION
        )  # Default
        assert skill.tags == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_TAGS  # Default
        assert skill.examples == ["Custom example"]

    def test_get_skill_with_empty_a2a_config(self) -> None:
        """Test that skill uses defaults when a2a config is None."""
        config = A2AAgentConfig(a2a=None)
        skill = _get_skill_generate_ui_components(config)

        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME
        assert skill.description == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION

    def test_get_skill_with_empty_skills_config(self) -> None:
        """Test that skill uses defaults when skills config is None."""
        config = A2AAgentConfig(a2a=A2AConfig(skills=None))
        skill = _get_skill_generate_ui_components(config)

        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME
        assert skill.description == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION

    def test_get_skill_with_empty_generate_ui_components(self) -> None:
        """Test that skill uses defaults when generate_ui_components is None."""
        config = A2AAgentConfig(
            a2a=A2AConfig(skills=A2AAgentSkills(generate_ui_components=None))
        )
        skill = _get_skill_generate_ui_components(config)

        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_NAME
        assert skill.description == DEFAULT_SKILL_GENERATE_UI_COMPONENTS_DESCRIPTION


class TestCreateAgentCard:
    """Tests for create_agent_card function."""

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_with_defaults(self, mock_version: Mock) -> None:
        """Test that agent card uses default values when no config is provided."""
        mock_version.return_value = "1.2.3"
        config = A2AAgentConfig()
        real_url = "https://example.com/agent"

        card = create_agent_card(config, real_url)

        assert isinstance(card, AgentCard)
        assert card.name == DEFAULT_AGENT_CARD_NAME
        assert card.description == DEFAULT_AGENT_CARD_DESCRIPTION
        assert card.url == real_url
        assert card.version == "1.2.3"
        assert card.default_input_modes == ["text"]
        assert card.default_output_modes == ["text"]
        assert isinstance(card.capabilities, AgentCapabilities)
        assert card.capabilities.streaming is True
        assert len(card.skills) == 1
        assert card.skills[0].id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert card.supports_authenticated_extended_card is False

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_with_full_config(self, mock_version: Mock) -> None:
        """Test that agent card uses all provided config values."""
        mock_version.return_value = "2.0.0"
        card_info = A2AAgentCardInfo(
            name="Custom Agent Name",
            description="Custom agent description",
            url="https://custom.example.com/agent",
        )
        config = A2AAgentConfig(a2a=A2AConfig(agent_card=card_info))
        real_url = "https://example.com/agent"

        card = create_agent_card(config, real_url)

        assert card.name == "Custom Agent Name"
        assert card.description == "Custom agent description"
        assert card.url == "https://custom.example.com/agent"
        assert card.version == "2.0.0"

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_with_partial_config(self, mock_version: Mock) -> None:
        """Test that agent card uses provided values and defaults for missing ones."""
        mock_version.return_value = "1.5.0"
        card_info = A2AAgentCardInfo(
            name="Partial Config Agent",
            description=None,  # Should use default
            url=None,  # Should use real_url
        )
        config = A2AAgentConfig(a2a=A2AConfig(agent_card=card_info))
        real_url = "https://real.example.com/agent"

        card = create_agent_card(config, real_url)

        assert card.name == "Partial Config Agent"
        assert card.description == DEFAULT_AGENT_CARD_DESCRIPTION
        assert card.url == real_url
        assert card.version == "1.5.0"

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_url_override(self, mock_version: Mock) -> None:
        """Test that agent card URL can be overridden in config."""
        mock_version.return_value = "1.0.0"
        card_info = A2AAgentCardInfo(url="https://proxy.example.com/agent")
        config = A2AAgentConfig(a2a=A2AConfig(agent_card=card_info))
        real_url = "https://internal.example.com/agent"

        card = create_agent_card(config, real_url)

        assert card.url == "https://proxy.example.com/agent"

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_with_empty_a2a_config(self, mock_version: Mock) -> None:
        """Test that agent card uses defaults when a2a config is None."""
        mock_version.return_value = "1.0.0"
        config = A2AAgentConfig(a2a=None)
        real_url = "https://example.com/agent"

        card = create_agent_card(config, real_url)

        assert card.name == DEFAULT_AGENT_CARD_NAME
        assert card.url == real_url

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_with_empty_agent_card_config(
        self, mock_version: Mock
    ) -> None:
        """Test that agent card uses defaults when agent_card config is None."""
        mock_version.return_value = "1.0.0"
        config = A2AAgentConfig(a2a=A2AConfig(agent_card=None))
        real_url = "https://example.com/agent"

        card = create_agent_card(config, real_url)

        assert card.name == DEFAULT_AGENT_CARD_NAME
        assert card.url == real_url

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_includes_skill(self, mock_version: Mock) -> None:
        """Test that agent card includes the generate_ui_components skill."""
        mock_version.return_value = "1.0.0"
        skill_info = A2AAgentSkill(
            name="Custom Skill Name",
            description="Custom skill description",
        )
        config = A2AAgentConfig(
            a2a=A2AConfig(skills=A2AAgentSkills(generate_ui_components=skill_info))
        )
        real_url = "https://example.com/agent"

        card = create_agent_card(config, real_url)

        assert len(card.skills) == 1
        skill = card.skills[0]
        assert isinstance(skill, AgentSkill)
        assert skill.id == SKILL_ID_GENERATE_UI_COMPONENTS
        assert skill.name == "Custom Skill Name"
        assert skill.description == "Custom skill description"

    @patch("next_gen_ui_a2a.agent_card._get_package_version")
    def test_create_agent_card_capabilities(self, mock_version: Mock) -> None:
        """Test that agent card has correct capabilities."""
        mock_version.return_value = "1.0.0"
        config = A2AAgentConfig()
        real_url = "https://example.com/agent"

        card = create_agent_card(config, real_url)

        assert isinstance(card.capabilities, AgentCapabilities)
        assert card.capabilities.streaming is True

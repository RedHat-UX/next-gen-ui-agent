from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_strategy import trim_to_json
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
)


class TestGetAllowedComponents:
    """Test cases for get_allowed_components() method."""

    def test_no_config_uses_defaults(self):
        """Test that all default components are returned when no config is provided."""
        config = AgentConfig()
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        components = strategy.get_allowed_components()

        # Should include all default components
        assert "table" in components
        assert "one-card" in components
        assert "set-of-cards" in components
        assert "chart-bar" in components
        assert "chart-line" in components
        assert "chart-pie" in components
        assert "chart-donut" in components
        assert "image" in components
        assert "video-player" in components
        assert len(components) >= 9  # At least these components

    def test_with_selectable_components_config(self):
        """Test that only configured components are returned."""
        config = AgentConfig(selectable_components={"table", "chart-bar", "one-card"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        components = strategy.get_allowed_components()

        assert components == {"table", "chart-bar", "one-card"}

    def test_with_data_type_and_components_config(self):
        """Test that data_type specific components are returned."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(component="chart-bar"),
                    ]
                )
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        components = strategy.get_allowed_components("movies")

        assert components == {"table", "chart-bar"}

    def test_with_data_type_empty_components(self):
        """Test that all default components are returned when data_type has empty components list."""
        config = AgentConfig(
            data_types={"movies": AgentConfigDataType(components=None)}
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        components = strategy.get_allowed_components("movies")

        # Should fall back to all defaults
        assert "table" in components
        assert "chart-bar" in components
        assert len(components) > 5

    def test_without_data_type_uses_global_selection(self):
        """Test that global selection is used when data_type is None."""
        config = AgentConfig(
            selectable_components={"table", "one-card"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Call without data_type should use global selectable_components
        components = strategy.get_allowed_components(None)

        assert components == {"table", "one-card"}

    def test_with_unknown_data_type_uses_global_selection(self):
        """Test that global selection is used when data_type is unknown."""
        config = AgentConfig(
            selectable_components={"table", "chart-pie"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Call with unknown data_type should use global selectable_components
        components = strategy.get_allowed_components("unknown_type")

        assert components == {"table", "chart-pie"}


class TestGetAllowedComponentsDescription:
    """Test cases for get_allowed_components_description() method."""

    def test_no_config_uses_defaults(self):
        """Test that description includes all default components when no config is provided."""
        config = AgentConfig()
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description()

        # Should include descriptions for all default components
        assert "table" in description
        assert "one-card" in description
        assert "set-of-cards" in description
        assert "chart-bar" in description
        assert isinstance(description, str)
        assert len(description) > 100  # Should be a substantial description

    def test_with_selectable_components_config(self):
        """Test that description includes only configured components."""
        config = AgentConfig(selectable_components={"table", "chart-bar"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description()

        assert "table" in description
        assert "chart-bar" in description
        # Should not include components not in selectable_components
        assert (
            "set-of-cards" not in description or description.count("set-of-cards") == 0
        )

    def test_with_data_type_and_components_config(self):
        """Test that description includes data_type specific components."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(component="one-card"),
                    ]
                )
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description("movies")

        assert "table" in description
        assert "one-card" in description
        # Should not include chart components
        assert "chart-bar" not in description or "chart-bar" in description.lower()

    def test_with_data_type_empty_components(self):
        """Test that description includes all defaults when data_type has empty components."""
        config = AgentConfig(
            data_types={"movies": AgentConfigDataType(components=None)}
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description("movies")

        # Should fall back to all defaults
        assert "table" in description
        assert "chart-bar" in description
        assert len(description) > 100

    def test_without_data_type_uses_global_selection(self):
        """Test that global selection is used when data_type is None."""
        config = AgentConfig(
            selectable_components={"table", "one-card"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description(None)

        assert "table" in description
        assert "one-card" in description
        # Should not include chart-bar from data_type config
        assert "chart-bar" not in description

    def test_description_format(self):
        """Test that description has expected format with component descriptions."""
        config = AgentConfig(selectable_components={"table"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description()

        # Description should contain the component name and some description text
        assert "table" in description.lower()
        assert len(description) > 10  # Should have actual description text

    def test_chart_components_excluded_when_not_configured(self):
        """Test that chart components are excluded from description when not configured."""
        config = AgentConfig(selectable_components={"table", "one-card"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        description = strategy.get_allowed_components_description()

        # Check that no chart components are in the description
        # Note: We're checking for exact component names, not substrings
        lines = description.lower().split("\n")
        component_names = [line.split("-")[0].strip() for line in lines if "-" in line]

        assert "chart" not in " ".join(component_names) or all(
            "chart" not in comp for comp in component_names
        )


class TestGetSystemPrompt:
    """Test cases for get_system_prompt() method with data_type parameter."""

    def test_without_argument_returns_global_prompt(self):
        """Test that calling without argument returns global prompt (backward compatibility)."""
        config = AgentConfig(selectable_components={"table", "chart-bar"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        prompt = strategy.get_system_prompt()

        # Should include configured components
        assert "table" in prompt
        assert "chart-bar" in prompt
        # Should not include non-configured components
        assert "set-of-cards" not in prompt

    def test_with_none_argument_returns_global_prompt(self):
        """Test that calling with None explicitly returns global prompt."""
        config = AgentConfig(selectable_components={"one-card", "chart-pie"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        prompt = strategy.get_system_prompt(None)

        assert "one-card" in prompt
        assert "chart-pie" in prompt

    def test_with_data_type_returns_specific_prompt(self):
        """Test that calling with data_type returns data-type-specific prompt."""
        config = AgentConfig(
            selectable_components={"table", "chart-bar"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="chart-line"),
                        AgentConfigComponent(component="chart-pie"),
                    ]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        movies_prompt = strategy.get_system_prompt("movies")
        global_prompt = strategy.get_system_prompt(None)

        # Should include data-type-specific components in AVAILABLE UI COMPONENTS section
        assert "chart-line" in movies_prompt
        assert "chart-pie" in movies_prompt

        # Prompts should be different
        assert movies_prompt != global_prompt

        # Global prompt should include its configured components
        assert "chart-bar" in global_prompt

    def test_with_unknown_data_type_returns_global_prompt(self):
        """Test that unknown data_type falls back to global prompt."""
        config = AgentConfig(
            selectable_components={"table"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        unknown_prompt = strategy.get_system_prompt("unknown_type")

        # Should fall back to global selectable_components
        assert "table" in unknown_prompt
        assert "chart-bar" not in unknown_prompt

    def test_different_data_types_return_different_prompts(self):
        """Test that different data types return different prompts."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="chart-bar"),
                        AgentConfigComponent(component="chart-line"),
                    ]
                ),
                "orders": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="chart-pie"),
                        AgentConfigComponent(component="chart-donut"),
                    ]
                ),
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        movies_prompt = strategy.get_system_prompt("movies")
        orders_prompt = strategy.get_system_prompt("orders")

        # Movies prompt should have chart-bar and chart-line
        assert "chart-bar" in movies_prompt
        assert "chart-line" in movies_prompt

        # Orders prompt should have chart-pie and chart-donut
        assert "chart-pie" in orders_prompt
        assert "chart-donut" in orders_prompt

        # Prompts should be different
        assert movies_prompt != orders_prompt

    def test_no_config_returns_all_defaults(self):
        """Test that no config returns prompt with all default components."""
        config = AgentConfig()
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        prompt = strategy.get_system_prompt()

        # Should include all default components
        assert "table" in prompt
        assert "chart-bar" in prompt
        assert "one-card" in prompt
        assert len(prompt) > 500  # Should be substantial

    def test_empty_data_type_components_uses_defaults(self):
        """Test that empty components list for data_type uses all defaults."""
        config = AgentConfig(
            data_types={"movies": AgentConfigDataType(components=None)}
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        movies_prompt = strategy.get_system_prompt("movies")

        # Should fall back to all defaults
        assert "table" in movies_prompt
        assert "chart-bar" in movies_prompt
        assert "one-card" in movies_prompt

    def test_caching_works_for_data_types(self):
        """Test that prompts are cached for performance."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                )
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Call twice with same data_type
        prompt1 = strategy.get_system_prompt("movies")
        prompt2 = strategy.get_system_prompt("movies")

        # Should return the same prompt (from cache)
        assert prompt1 == prompt2
        assert prompt1 is prompt2  # Same object reference due to caching


class TestTrimToJson:
    """Test cases for trim_to_json method."""

    def test_trim_to_json_basic_object(self):
        text = '{"name": "John", "age": 30}'
        result = trim_to_json(text)
        assert result == '{"name": "John", "age": 30}'

    def test_trim_to_json_basic_array(self):
        text = '["item1", "item2", "item3"]'
        result = trim_to_json(text)
        assert result == '["item1", "item2", "item3"]'

    def test_trim_to_json_around_object(self):
        text = 'Prefix {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} suffix'
        result = trim_to_json(text)
        assert (
            result
            == '{"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}'
        )

    def test_trim_to_json_around_array(self):
        text = 'Prefix [ {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} ] suffix'
        result = trim_to_json(text)
        assert (
            result
            == '[ {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} ]'
        )

    def test_trim_to_json_textonly(self):
        text = "Prefix suffix"
        result = trim_to_json(text)
        assert result == "Prefix suffix"

    def test_trim_to_json_text_with_think(self):
        text = 'Prefix </think> other text { "name": "John" } suffix'
        result = trim_to_json(text)
        assert result == '{ "name": "John" }'

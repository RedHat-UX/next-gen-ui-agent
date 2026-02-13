import pytest
from langchain_core.language_models import FakeMessagesListChatModel
from next_gen_ui_agent.component_selection_llm_onestep import (
    OnestepLLMCallComponentSelectionStrategy,
)
from next_gen_ui_agent.component_selection_llm_strategy import trim_to_json
from next_gen_ui_agent.inference.langchain_inference import LangChainModelInference
from next_gen_ui_agent.types import (
    AgentConfig,
    AgentConfigComponent,
    AgentConfigDataType,
    InputDataInternal,
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


class TestResolveAllowedComponentsCaching:
    """Test cases for _resolve_allowed_components_and_metadata caching mechanism."""

    def test_cache_returns_same_result_for_same_data_type(self):
        """Test that calling with same data_type returns cached result."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="chart-bar"),
                        AgentConfigComponent(component="table"),
                    ]
                )
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # First call - should compute and cache
        result1 = strategy._resolve_allowed_components_and_metadata("movies")

        # Second call - should return cached result
        result2 = strategy._resolve_allowed_components_and_metadata("movies")

        # Results should be identical (same object reference)
        assert result1 is result2
        assert result1[0] == result2[0]  # allowed_components
        assert result1[1] is result2[1]  # metadata

    def test_cache_returns_same_result_for_none_data_type(self):
        """Test that calling with None data_type returns cached result."""
        config = AgentConfig(selectable_components={"table", "one-card", "chart-bar"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # First call - should compute and cache
        result1 = strategy._resolve_allowed_components_and_metadata(None)

        # Second call - should return cached result
        result2 = strategy._resolve_allowed_components_and_metadata(None)

        # Results should be identical (same object reference)
        assert result1 is result2
        assert result1[0] == result2[0]
        assert result1[1] is result2[1]

    def test_cache_separates_different_data_types(self):
        """Test that different data_types don't get mixed up in cache."""
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
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(component="one-card"),
                    ]
                ),
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Get results for different data_types
        movies_result = strategy._resolve_allowed_components_and_metadata("movies")
        orders_result = strategy._resolve_allowed_components_and_metadata("orders")

        # Results should be different
        assert movies_result != orders_result
        assert movies_result[0] != orders_result[0]  # Different allowed components

        # Movies should have chart components
        assert "chart-bar" in movies_result[0]
        assert "chart-line" in movies_result[0]
        assert "table" not in movies_result[0]
        assert "one-card" not in movies_result[0]

        # Orders should have table and card components
        assert "table" in orders_result[0]
        assert "one-card" in orders_result[0]
        assert "chart-bar" not in orders_result[0]
        assert "chart-line" not in orders_result[0]

    def test_cache_separates_none_from_actual_data_types(self):
        """Test that None data_type is cached separately from actual data_types."""
        config = AgentConfig(
            selectable_components={"table", "one-card"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="chart-bar"),
                        AgentConfigComponent(component="chart-pie"),
                    ]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Get results for None and a data_type
        none_result = strategy._resolve_allowed_components_and_metadata(None)
        movies_result = strategy._resolve_allowed_components_and_metadata("movies")

        # Results should be different
        assert none_result != movies_result
        assert none_result[0] != movies_result[0]

        # None should use global selectable_components
        assert none_result[0] == {"table", "one-card"}

        # Movies should use data_type specific components
        assert movies_result[0] == {"chart-bar", "chart-pie"}

    def test_cache_handles_unknown_data_type_as_none(self):
        """Test that unknown data_type uses global config and is cached separately."""
        config = AgentConfig(
            selectable_components={"table", "chart-bar"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-pie")]
                )
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Get results for unknown data_type
        unknown1 = strategy._resolve_allowed_components_and_metadata("unknown_type")
        unknown2 = strategy._resolve_allowed_components_and_metadata("unknown_type")
        movies = strategy._resolve_allowed_components_and_metadata("movies")

        # Unknown should be cached
        assert unknown1 is unknown2

        # Unknown should use global config (not movies config)
        assert unknown1[0] == {"table", "chart-bar"}
        assert movies[0] == {"chart-pie"}

    def test_cache_persists_across_multiple_calls(self):
        """Test that cache persists correctly across multiple interleaved calls."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                ),
                "orders": AgentConfigDataType(
                    components=[AgentConfigComponent(component="table")]
                ),
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Make interleaved calls
        movies1 = strategy._resolve_allowed_components_and_metadata("movies")
        orders1 = strategy._resolve_allowed_components_and_metadata("orders")
        movies2 = strategy._resolve_allowed_components_and_metadata("movies")
        orders2 = strategy._resolve_allowed_components_and_metadata("orders")
        movies3 = strategy._resolve_allowed_components_and_metadata("movies")

        # All calls for same data_type should return same cached object
        assert movies1 is movies2
        assert movies2 is movies3
        assert orders1 is orders2

        # Different data_types should return different objects
        assert movies1 is not orders1

    def test_cache_contains_correct_data_for_each_key(self):
        """Test that cached data is correct for each cache key."""
        config = AgentConfig(
            selectable_components={"table", "one-card"},
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="chart-bar"),
                        AgentConfigComponent(component="chart-line"),
                    ]
                ),
                "orders": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(component="table"),
                        AgentConfigComponent(component="set-of-cards"),
                    ]
                ),
            },
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Populate cache
        strategy._resolve_allowed_components_and_metadata(None)
        strategy._resolve_allowed_components_and_metadata("movies")
        strategy._resolve_allowed_components_and_metadata("orders")

        # Verify cache contents
        assert None in strategy._allowed_components_cache
        assert "movies" in strategy._allowed_components_cache
        assert "orders" in strategy._allowed_components_cache

        # Verify each cached entry has correct components
        none_cached = strategy._allowed_components_cache[None]
        assert none_cached[0] == {"table", "one-card"}

        movies_cached = strategy._allowed_components_cache["movies"]
        assert movies_cached[0] == {"chart-bar", "chart-line"}

        orders_cached = strategy._allowed_components_cache["orders"]
        assert orders_cached[0] == {"table", "set-of-cards"}

    def test_cache_initialization(self):
        """Test that cache is properly initialized and populated during __init__."""
        config = AgentConfig()
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Cache should exist and be a dict
        assert hasattr(strategy, "_allowed_components_cache")
        assert isinstance(strategy._allowed_components_cache, dict)

        # Cache should have one entry for None (populated during __init__)
        assert len(strategy._allowed_components_cache) == 1
        assert None in strategy._allowed_components_cache

    def test_cache_grows_as_data_types_are_accessed(self):
        """Test that cache grows appropriately as different data_types are accessed."""
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[AgentConfigComponent(component="chart-bar")]
                ),
                "orders": AgentConfigDataType(
                    components=[AgentConfigComponent(component="table")]
                ),
                "products": AgentConfigDataType(
                    components=[AgentConfigComponent(component="one-card")]
                ),
            }
        )
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Initially has one entry for None (populated during __init__)
        assert len(strategy._allowed_components_cache) == 1
        assert None in strategy._allowed_components_cache

        # Access movies
        strategy._resolve_allowed_components_and_metadata("movies")
        assert len(strategy._allowed_components_cache) == 2
        assert "movies" in strategy._allowed_components_cache

        # Access orders
        strategy._resolve_allowed_components_and_metadata("orders")
        assert len(strategy._allowed_components_cache) == 3
        assert "orders" in strategy._allowed_components_cache

        # Re-access None (should not increase size, already cached)
        strategy._resolve_allowed_components_and_metadata(None)
        assert len(strategy._allowed_components_cache) == 3

        # Re-access movies (should not increase size)
        strategy._resolve_allowed_components_and_metadata("movies")
        assert len(strategy._allowed_components_cache) == 3

        # Access products (should increase size)
        strategy._resolve_allowed_components_and_metadata("products")
        assert len(strategy._allowed_components_cache) == 4
        assert "products" in strategy._allowed_components_cache


class TestComponentValidation:
    """Test cases for component validation in select_component method."""

    @pytest.mark.asyncio
    async def test_select_component_rejects_invalid_component_for_data_type(self):
        """Test that selecting an invalid component for data_type raises ValueError."""
        # Configure to only allow table and one-card for "movies" data_type
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

        # Mock LLM response that returns chart-bar (not allowed for movies)
        invalid_response = """{
            "title": "Movie Revenue",
            "reasonForTheComponentSelection": "Chart is good for comparison",
            "confidenceScore": "90%",
            "component": "chart-bar",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
                {"name": "Revenue", "data_path": "movies[*].revenue"}
            ]
        }"""

        msg = {"type": "assistant", "content": invalid_response}
        llm = FakeMessagesListChatModel(responses=[msg])
        inference = LangChainModelInference(llm)

        input_data = InputDataInternal(
            {
                "id": "1",
                "data": '[{"title": "Movie1", "revenue": 1000}]',
                "type": "movies",
            }
        )

        # Should raise ValueError because chart-bar is not allowed for movies
        with pytest.raises(ValueError) as exc_info:
            await strategy.select_component(inference, "Show movies", input_data)

        # Verify error message content
        error_msg = str(exc_info.value)
        assert "chart-bar" in error_msg
        assert "not allowed" in error_msg
        assert "movies" in error_msg
        assert "table" in error_msg
        assert "one-card" in error_msg

    @pytest.mark.asyncio
    async def test_select_component_accepts_valid_component_for_data_type(self):
        """Test that selecting a valid component for data_type succeeds."""
        # Configure to only allow table and one-card for "movies" data_type
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

        # Mock LLM response that returns table (allowed for movies)
        valid_response = """{
            "title": "Movies List",
            "reasonForTheComponentSelection": "Table is good for multiple items",
            "confidenceScore": "90%",
            "component": "table",
            "fields": [
                {"name": "Title", "data_path": "movies[*].title"},
                {"name": "Year", "data_path": "movies[*].year"}
            ]
        }"""

        msg = {"type": "assistant", "content": valid_response}
        llm = FakeMessagesListChatModel(responses=[msg])
        inference = LangChainModelInference(llm)

        input_data = InputDataInternal(
            {
                "id": "1",
                "data": '[{"title": "Movie1", "year": 2020}]',
                "type": "movies",
            }
        )

        # Should succeed because table is allowed for movies
        result = await strategy.select_component(inference, "Show movies", input_data)
        assert result.component == "table"
        assert result.input_data_type == "movies"

    @pytest.mark.asyncio
    async def test_select_component_validates_against_global_config_when_no_data_type(
        self,
    ):
        """Test that component validation uses global config when data_type is None."""
        # Configure global selection to only allow table
        config = AgentConfig(selectable_components={"table"})
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Mock LLM response that returns chart-bar (not in global config)
        invalid_response = """{
            "title": "Chart",
            "reasonForTheComponentSelection": "Chart for comparison",
            "confidenceScore": "90%",
            "component": "chart-bar",
            "fields": [
                {"name": "Item", "data_path": "items[*].name"},
                {"name": "Value", "data_path": "items[*].value"}
            ]
        }"""

        msg = {"type": "assistant", "content": invalid_response}
        llm = FakeMessagesListChatModel(responses=[msg])
        inference = LangChainModelInference(llm)

        input_data = InputDataInternal(
            {"id": "1", "data": '[{"name": "Item1", "value": 100}]'}
        )

        # Should raise ValueError because chart-bar is not in global config
        with pytest.raises(ValueError) as exc_info:
            await strategy.select_component(inference, "Show data", input_data)

        error_msg = str(exc_info.value)
        assert "chart-bar" in error_msg
        assert "not allowed" in error_msg
        assert "table" in error_msg

    @pytest.mark.asyncio
    async def test_select_component_accepts_any_default_when_no_restrictions(self):
        """Test that any default component is accepted when no restrictions are configured."""
        # No restrictions configured - should allow all defaults
        config = AgentConfig()
        strategy = OnestepLLMCallComponentSelectionStrategy(config)

        # Mock LLM response with chart-bar (should be in defaults)
        valid_response = """{
            "title": "Chart",
            "reasonForTheComponentSelection": "Chart for comparison",
            "confidenceScore": "90%",
            "component": "chart-bar",
            "fields": [
                {"name": "Item", "data_path": "items[*].name"},
                {"name": "Value", "data_path": "items[*].value"}
            ]
        }"""

        msg = {"type": "assistant", "content": valid_response}
        llm = FakeMessagesListChatModel(responses=[msg])
        inference = LangChainModelInference(llm)

        input_data = InputDataInternal(
            {"id": "1", "data": '[{"name": "Item1", "value": 100}]'}
        )

        # Should succeed because chart-bar is in defaults and no restrictions
        result = await strategy.select_component(inference, "Show chart", input_data)
        assert result.component == "chart-bar"

import pytest
from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.component_selection_common import (
    CHART_COMPONENTS,
    COMPONENT_METADATA,
)

from .component_selection_llm_twostep import TwostepLLMCallComponentSelectionStrategy


class TestBuildStep1selectSystemPrompt:
    """Test _build_step1select_system_prompt method."""

    def test_all_components_when_none(self):
        """Test that all components are included when selectable_components is None."""
        config = AgentConfig(selectable_components=None)
        strategy = TwostepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_step1select_system_prompt(
            None, strategy._base_metadata
        )

        # Should include all components
        for component in COMPONENT_METADATA.keys():
            assert component in prompt

        # Should include chart instructions
        assert "CHART TYPES" in prompt

        # Should include examples
        assert "Response example" in prompt

    def test_basic_components_only(self):
        """Test with only basic (non-chart) components."""
        basic_components = {"one-card", "table", "set-of-cards"}
        config = AgentConfig(selectable_components=basic_components)
        strategy = TwostepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_step1select_system_prompt(
            basic_components, strategy._base_metadata
        )

        # Should include selected basic components
        assert "one-card" in prompt
        assert "table" in prompt
        assert "set-of-cards" in prompt

        # Should NOT include chart components
        for chart_comp in CHART_COMPONENTS:
            assert chart_comp not in prompt

        # Should NOT include chart instructions
        assert "CHART TYPES" not in prompt

        # Should include examples for basic components
        assert "Response example" in prompt

    def test_with_chart_components(self):
        """Test with chart components included."""
        components_with_charts = {"table", "chart-bar", "chart-line"}
        config = AgentConfig(selectable_components=components_with_charts)
        strategy = TwostepLLMCallComponentSelectionStrategy(config)
        prompt = strategy._build_step1select_system_prompt(
            components_with_charts, strategy._base_metadata
        )

        # Should include selected components
        assert "table" in prompt
        assert "chart-bar" in prompt
        assert "chart-line" in prompt

        # Should include chart instructions
        assert "CHART TYPES" in prompt
        assert "FIELDS BY CHART TYPE" in prompt

        # Should NOT include chart components that weren't selected
        assert "chart-pie" not in prompt
        assert "chart-donut" not in prompt

        # Should include examples
        assert "Response example" in prompt

    def test_with_component_metadata_overrides(self):
        """Test that component metadata overrides are applied to system prompt."""
        from next_gen_ui_agent.types import (
            AgentConfigPrompt,
            AgentConfigPromptComponent,
        )

        # Create config with overrides
        config = AgentConfig(
            prompt=AgentConfigPrompt(
                components={
                    "table": AgentConfigPromptComponent(
                        description="CUSTOM_TABLE_DESCRIPTION for twostep testing"
                    ),
                    "chart-bar": AgentConfigPromptComponent(
                        chart_description="CUSTOM_BAR_CHART_DESCRIPTION for twostep testing"
                    ),
                }
            )
        )

        # Create strategy with overrides
        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Get the step1select system prompt
        prompt = strategy.get_system_prompt()

        # Verify custom descriptions are in the prompt
        assert "CUSTOM_TABLE_DESCRIPTION for twostep testing" in prompt
        assert "CUSTOM_BAR_CHART_DESCRIPTION for twostep testing" in prompt

        # Verify original descriptions are NOT in the prompt
        assert COMPONENT_METADATA["table"]["description"] not in prompt
        assert COMPONENT_METADATA["chart-bar"]["chart_description"] not in prompt


class TestSystemPromptCachingTwostep:
    """Tests for system prompt caching mechanism in twostep strategy."""

    def test_cache_hit_for_same_data_type(self):
        """Test that cache is used for repeated calls with same data_type."""
        from unittest.mock import patch

        from next_gen_ui_agent.types import (
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="Movies table"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

        # Cache starts with one entry (None) from __init__
        initial_cache_size = len(strategy._system_prompt_step1select_cache)
        assert None in strategy._system_prompt_step1select_cache

        # Spy on _build_step1select_system_prompt
        with patch.object(
            strategy,
            "_build_step1select_system_prompt",
            wraps=strategy._build_step1select_system_prompt,
        ) as mock_build:
            # Call twice with same data_type
            prompt1 = strategy._get_or_build_step1select_system_prompt("movies")
            prompt2 = strategy._get_or_build_step1select_system_prompt("movies")

            # Build should only be called once (for "movies")
            assert mock_build.call_count == 1

            # Should return same object (not just equal)
            assert prompt1 is prompt2

            # Cache should have "movies" entry plus initial None
            assert "movies" in strategy._system_prompt_step1select_cache
            assert (
                len(strategy._system_prompt_step1select_cache) == initial_cache_size + 1
            )

    def test_global_selection_uses_none_key(self):
        """Test that global selection uses None as cache key."""
        config = AgentConfig(selectable_components={"table", "chart-bar"})

        strategy = TwostepLLMCallComponentSelectionStrategy(config=config)

        # Call with None (global selection)
        prompt1 = strategy._get_or_build_step1select_system_prompt(None)
        prompt2 = strategy._get_or_build_step1select_system_prompt(None)

        # Should use None as cache key
        assert None in strategy._system_prompt_step1select_cache

        # Should return same object
        assert prompt1 is prompt2


class TestSkipStep2configureLogic:
    """Test that step2configure is correctly skipped for HBCs and pre-configured components."""

    @pytest.mark.asyncio
    async def test_skip_step2configure_for_hbc(self):
        """Test that step2configure is skipped when an HBC (hand-build component) is selected."""
        from next_gen_ui_agent.inference.inference_base import InferenceBase
        from next_gen_ui_agent.types import (
            AgentConfig,
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        # Create config with an HBC (chart-bar is not in DYNAMIC_COMPONENT_NAMES)
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="chart-bar",
                            prompt=AgentConfigPromptComponent(
                                description="Bar chart for movies"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Mock inference that returns HBC selection
        class MockInference(InferenceBase):
            async def call_model(self, system_prompt: str, user_prompt: str) -> str:
                return '{"component": "chart-bar", "title": "Movies", "reasonForTheComponentSelection": "test", "confidenceScore": "90%"}'

        inference = MockInference()
        result = await strategy.perform_inference(
            inference=inference,
            user_prompt="Show me movies",
            json_data={"movies": []},
            input_data_id="test-1",
            data_type="movies",
        )

        # step2configure should be skipped, so only 1 output (step1select result)
        assert len(result["outputs"]) == 1
        # Only 1 LLM interaction (step1select only)
        assert len(result["llm_interactions"]) == 1
        assert result["llm_interactions"][0]["step"] == "component_selection"

    @pytest.mark.asyncio
    async def test_skip_step2configure_for_preconfigured_component(self):
        """Test that step2configure is skipped for pre-configured dynamic components (llm_configure=False)."""
        from next_gen_ui_agent.inference.inference_base import InferenceBase
        from next_gen_ui_agent.types import (
            AgentConfig,
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigDynamicComponentConfiguration,
            DataField,
        )

        # Create config with pre-configured component (llm_configure=False)
        config = AgentConfig(
            data_types={
                "orders": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            llm_configure=False,
                            configuration=AgentConfigDynamicComponentConfiguration(
                                title="Orders",
                                fields=[
                                    DataField(name="Order ID", data_path="orders[*].id")
                                ],
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Mock inference that returns table selection
        class MockInference(InferenceBase):
            async def call_model(self, system_prompt: str, user_prompt: str) -> str:
                return '{"component": "table", "title": "Orders", "reasonForTheComponentSelection": "test", "confidenceScore": "90%"}'

        inference = MockInference()
        result = await strategy.perform_inference(
            inference=inference,
            user_prompt="Show me orders",
            json_data={"orders": []},
            input_data_id="test-1",
            data_type="orders",
        )

        # step2configure should be skipped, so only 1 output (step1select result)
        assert len(result["outputs"]) == 1
        # Only 1 LLM interaction (step1select only)
        assert len(result["llm_interactions"]) == 1
        assert result["llm_interactions"][0]["step"] == "component_selection"

    @pytest.mark.asyncio
    async def test_execute_step2configure_for_dynamic_component(self):
        """Test that step2configure is executed for normal dynamic components."""
        from next_gen_ui_agent.inference.inference_base import InferenceBase
        from next_gen_ui_agent.types import (
            AgentConfig,
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        # Create config with dynamic component (table is in DYNAMIC_COMPONENT_NAMES)
        config = AgentConfig(
            data_types={
                "products": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="Table for products"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Mock inference that returns different responses for step1select and step2configure
        call_count = 0

        class MockInference(InferenceBase):
            async def call_model(self, system_prompt: str, user_prompt: str) -> str:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    # step1select: component selection
                    return '{"component": "table", "title": "Products", "reasonForTheComponentSelection": "test", "confidenceScore": "90%"}'
                else:
                    # step2configure: field selection
                    return '[{"name": "Name", "data_path": "products[*].name"}]'

        inference = MockInference()
        result = await strategy.perform_inference(
            inference=inference,
            user_prompt="Show me products",
            json_data={"products": []},
            input_data_id="test-1",
            data_type="products",
        )

        # step2configure should be executed, so 2 outputs (step1select and step2configure)
        assert len(result["outputs"]) == 2
        # 2 LLM interactions (both steps)
        assert len(result["llm_interactions"]) == 2
        assert result["llm_interactions"][0]["step"] == "component_selection"
        assert result["llm_interactions"][1]["step"] == "field_selection"


class TestParseInferenceOutputWithSkippedStep2configure:
    """Test that parse_inference_output correctly handles cases where step2configure is skipped."""

    def test_parse_output_for_hbc_with_skipped_step2configure(self):
        """Test parsing when step2configure is skipped for HBC (only step1select output, no fields)."""
        from next_gen_ui_agent.types import AgentConfig

        config = AgentConfig()
        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Simulate result from step1select only (HBC case)
        inference_result = {
            "outputs": [
                '{"component": "chart-bar", "title": "Movie Revenue", "reasonForTheComponentSelection": "User wants bar chart", "confidenceScore": "95%"}'
            ],
            "llm_interactions": [
                {
                    "step": "component_selection",
                    "system_prompt": "test",
                    "user_prompt": "test",
                    "raw_response": "test",
                }
            ],
        }

        result = strategy.parse_infernce_output(inference_result, "test-id-1")

        # Verify parsed result
        assert result.id == "test-id-1"
        assert result.component == "chart-bar"
        assert result.title == "Movie Revenue"
        assert result.reasonForTheComponentSelection == "User wants bar chart"
        assert result.confidenceScore == "95%"
        # Fields should be empty list when step2configure is skipped
        assert result.fields == []
        # LLM interactions should be preserved
        assert len(result.llm_interactions) == 1
        assert result.llm_interactions[0]["step"] == "component_selection"

    def test_parse_output_for_preconfigured_component_with_skipped_step2configure(self):
        """Test parsing when step2configure is skipped for pre-configured dynamic component."""
        from next_gen_ui_agent.types import AgentConfig

        config = AgentConfig()
        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Simulate result from step1select only (pre-configured table)
        inference_result = {
            "outputs": [
                '{"component": "table", "title": "Orders", "reasonForTheComponentSelection": "Pre-configured table", "confidenceScore": "90%"}'
            ],
            "llm_interactions": [
                {
                    "step": "component_selection",
                    "system_prompt": "test",
                    "user_prompt": "test",
                    "raw_response": "test",
                }
            ],
        }

        result = strategy.parse_infernce_output(inference_result, "test-id-2")

        # Verify parsed result
        assert result.id == "test-id-2"
        assert result.component == "table"
        assert result.title == "Orders"
        assert result.reasonForTheComponentSelection == "Pre-configured table"
        assert result.confidenceScore == "90%"
        # Fields should be empty list (will be merged with pre-config later by caller)
        assert result.fields == []
        # LLM interactions should be preserved
        assert len(result.llm_interactions) == 1

    def test_parse_output_for_dynamic_component_with_step2configure(self):
        """Test parsing when step2configure is executed for normal dynamic component."""
        from next_gen_ui_agent.types import AgentConfig

        config = AgentConfig()
        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Simulate result from both steps (normal dynamic component)
        inference_result = {
            "outputs": [
                '{"component": "table", "title": "Products", "reasonForTheComponentSelection": "Best for tabular data", "confidenceScore": "92%"}',
                '[{"name": "Product Name", "data_path": "products[*].name"}, {"name": "Price", "data_path": "products[*].price"}]',
            ],
            "llm_interactions": [
                {
                    "step": "component_selection",
                    "system_prompt": "test1",
                    "user_prompt": "test1",
                    "raw_response": "test1",
                },
                {
                    "step": "field_selection",
                    "system_prompt": "test2",
                    "user_prompt": "test2",
                    "raw_response": "test2",
                },
            ],
        }

        result = strategy.parse_infernce_output(inference_result, "test-id-3")

        # Verify parsed result
        assert result.id == "test-id-3"
        assert result.component == "table"
        assert result.title == "Products"
        assert result.reasonForTheComponentSelection == "Best for tabular data"
        assert result.confidenceScore == "92%"
        # Fields should be populated from step2configure
        assert len(result.fields) == 2
        assert result.fields[0].name == "Product Name"
        assert result.fields[0].data_path == "products[*].name"
        assert result.fields[1].name == "Price"
        assert result.fields[1].data_path == "products[*].price"
        # Both LLM interactions should be preserved
        assert len(result.llm_interactions) == 2
        assert result.llm_interactions[0]["step"] == "component_selection"
        assert result.llm_interactions[1]["step"] == "field_selection"

    def test_parse_output_handles_empty_fields_array(self):
        """Test that empty fields array is handled correctly when step2configure is skipped."""
        from next_gen_ui_agent.types import AgentConfig

        config = AgentConfig()
        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Result with only step 1 output
        inference_result = {
            "outputs": [
                '{"component": "one-card", "title": "Order Details", "reasonForTheComponentSelection": "Single item", "confidenceScore": "88%"}'
            ],
            "llm_interactions": [
                {
                    "step": "component_selection",
                    "system_prompt": "test",
                    "user_prompt": "test",
                    "raw_response": "test",
                }
            ],
        }

        result = strategy.parse_infernce_output(inference_result, "test-id-4")

        # Empty fields should not cause validation errors
        assert result.fields == []
        assert isinstance(result.fields, list)
        assert result.component == "one-card"


class TestEndToEndFlowWithSkippedStep2configure:
    """End-to-end tests for complete flow: perform_inference + parse_inference_output."""

    @pytest.mark.asyncio
    async def test_e2e_hbc_skip_step2configure_and_parse(self):
        """Test complete flow for HBC: skip step2configure and parse result correctly."""
        from next_gen_ui_agent.inference.inference_base import InferenceBase
        from next_gen_ui_agent.types import (
            AgentConfig,
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        # Create config with an HBC
        config = AgentConfig(
            data_types={
                "movies": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="chart-bar",
                            prompt=AgentConfigPromptComponent(
                                description="Bar chart for movies"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Mock inference
        class MockInference(InferenceBase):
            async def call_model(self, system_prompt: str, user_prompt: str) -> str:
                return '{"component": "chart-bar", "title": "Top Movies", "reasonForTheComponentSelection": "Best for comparison", "confidenceScore": "93%"}'

        inference = MockInference()

        # Perform inference (step2configure should be skipped)
        inference_result = await strategy.perform_inference(
            inference=inference,
            user_prompt="Show top movies",
            json_data={"movies": [{"title": "Movie1", "revenue": 100}]},
            input_data_id="test-hbc-1",
            data_type="movies",
        )

        # Parse the result
        parsed = strategy.parse_infernce_output(inference_result, "test-hbc-1")

        # Verify complete result
        assert parsed.id == "test-hbc-1"
        assert parsed.component == "chart-bar"
        assert parsed.title == "Top Movies"
        assert parsed.fields == []  # No fields for HBC
        assert len(parsed.llm_interactions) == 1  # Only step1select

    @pytest.mark.asyncio
    async def test_e2e_preconfigured_skip_step2configure_and_parse(self):
        """Test complete flow for pre-configured component: skip step2configure and parse."""
        from next_gen_ui_agent.inference.inference_base import InferenceBase
        from next_gen_ui_agent.types import (
            AgentConfig,
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigDynamicComponentConfiguration,
            DataField,
        )

        # Create config with pre-configured table
        config = AgentConfig(
            data_types={
                "orders": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            llm_configure=False,
                            configuration=AgentConfigDynamicComponentConfiguration(
                                title="Orders",
                                fields=[
                                    DataField(
                                        name="Order ID", data_path="orders[*].id"
                                    ),
                                    DataField(
                                        name="Status", data_path="orders[*].status"
                                    ),
                                ],
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Mock inference
        class MockInference(InferenceBase):
            async def call_model(self, system_prompt: str, user_prompt: str) -> str:
                return '{"component": "table", "title": "All Orders", "reasonForTheComponentSelection": "Pre-configured", "confidenceScore": "90%"}'

        inference = MockInference()

        # Perform inference (step2configure should be skipped)
        inference_result = await strategy.perform_inference(
            inference=inference,
            user_prompt="Show orders",
            json_data={"orders": [{"id": "O1", "status": "shipped"}]},
            input_data_id="test-preconfig-1",
            data_type="orders",
        )

        # Parse the result
        parsed = strategy.parse_infernce_output(inference_result, "test-preconfig-1")

        # Verify result - fields should be empty (pre-config will be merged by caller)
        assert parsed.id == "test-preconfig-1"
        assert parsed.component == "table"
        assert parsed.title == "All Orders"
        assert parsed.fields == []  # Empty, pre-config merged separately
        assert len(parsed.llm_interactions) == 1  # Only step1select

    @pytest.mark.asyncio
    async def test_e2e_dynamic_component_with_step2configure_and_parse(self):
        """Test complete flow for dynamic component: execute step2configure and parse fields."""
        from next_gen_ui_agent.inference.inference_base import InferenceBase
        from next_gen_ui_agent.types import (
            AgentConfig,
            AgentConfigComponent,
            AgentConfigDataType,
            AgentConfigPromptComponent,
        )

        # Create config with normal dynamic component
        config = AgentConfig(
            data_types={
                "products": AgentConfigDataType(
                    components=[
                        AgentConfigComponent(
                            component="table",
                            prompt=AgentConfigPromptComponent(
                                description="Table for products"
                            ),
                        )
                    ]
                )
            }
        )

        strategy = TwostepLLMCallComponentSelectionStrategy(config)

        # Mock inference - different responses for step1select and step2configure
        call_count = 0

        class MockInference(InferenceBase):
            async def call_model(self, system_prompt: str, user_prompt: str) -> str:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return '{"component": "table", "title": "Product Catalog", "reasonForTheComponentSelection": "Best for lists", "confidenceScore": "94%"}'
                else:
                    return '[{"name": "Name", "data_path": "products[*].name"}, {"name": "Price", "data_path": "products[*].price"}, {"name": "Stock", "data_path": "products[*].stock"}]'

        inference = MockInference()

        # Perform inference (step2configure should be executed)
        inference_result = await strategy.perform_inference(
            inference=inference,
            user_prompt="Show products",
            json_data={"products": [{"name": "P1", "price": 10, "stock": 5}]},
            input_data_id="test-dynamic-1",
            data_type="products",
        )

        # Parse the result
        parsed = strategy.parse_infernce_output(inference_result, "test-dynamic-1")

        # Verify complete result with fields from step2configure
        assert parsed.id == "test-dynamic-1"
        assert parsed.component == "table"
        assert parsed.title == "Product Catalog"
        assert len(parsed.fields) == 3  # Fields from step2configure
        assert parsed.fields[0].name == "Name"
        assert parsed.fields[0].data_path == "products[*].name"
        assert parsed.fields[1].name == "Price"
        assert parsed.fields[2].name == "Stock"
        assert len(parsed.llm_interactions) == 2  # Both steps

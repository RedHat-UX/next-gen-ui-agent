from next_gen_ui_agent.component_selection_common import (
    ALL_COMPONENTS,
    CHART_COMPONENTS,
    COMPONENT_METADATA,
    build_chart_instructions,
    build_components_description,
    build_onestep_examples,
    build_twostep_step1_examples,
    build_twostep_step2_example,
    build_twostep_step2_extension,
)


class TestComponentMetadata:
    """Test COMPONENT_METADATA structure."""

    def test_all_components_present(self):
        """Test that all 10 components are present in COMPONENT_METADATA."""
        expected_components = set(ALL_COMPONENTS)
        assert set(COMPONENT_METADATA.keys()) == expected_components
        assert len(ALL_COMPONENTS) == 10

    def test_all_components_constant_consistency(self):
        """Test that ALL_COMPONENTS constant matches COMPONENT_METADATA keys."""
        assert set(ALL_COMPONENTS) == set(COMPONENT_METADATA.keys())
        # Ensure no duplicates in ALL_COMPONENTS
        assert len(ALL_COMPONENTS) == len(set(ALL_COMPONENTS))

    def test_chart_components_subset(self):
        """Test that CHART_COMPONENTS is a subset of ALL_COMPONENTS."""
        assert CHART_COMPONENTS.issubset(set(ALL_COMPONENTS))
        assert len(CHART_COMPONENTS) == 5

    def test_all_components_have_required_fields(self):
        """Test that all components have required fields."""
        required_fields = {
            "description",
            "onestep_example",
            "twostep_step1_example",
            "twostep_step2_example",
        }

        for component, metadata in COMPONENT_METADATA.items():
            for field in required_fields:
                assert (
                    field in metadata
                ), f"Component {component} missing required field {field}"
                assert metadata[field], f"Component {component} has empty {field}"

    def test_chart_components_have_chart_fields(self):
        """Test that chart components have chart-specific fields."""
        chart_specific_fields = {
            "chart_description",
            "chart_fields_spec",
            "chart_rules",
            "chart_inline_examples",
        }

        for chart_comp in CHART_COMPONENTS:
            for field in chart_specific_fields:
                assert (
                    field in COMPONENT_METADATA[chart_comp]
                ), f"Chart component {chart_comp} missing {field}"

    def test_non_chart_components_no_chart_fields(self):
        """Test that non-chart components don't have chart-specific fields."""
        non_chart_components = set(COMPONENT_METADATA.keys()) - CHART_COMPONENTS
        chart_specific_fields = {
            "chart_description",
            "chart_fields_spec",
            "chart_rules",
            "chart_inline_examples",
        }

        for component in non_chart_components:
            for field in chart_specific_fields:
                assert (
                    field not in COMPONENT_METADATA[component]
                ), f"Non-chart component {component} should not have {field}"


class TestBuildComponentsDescription:
    """Test build_components_description function."""

    def test_all_components_when_none(self):
        """Test that all components are included when allowed_components is None."""
        result = build_components_description(None)
        assert "one-card" in result
        assert "image" in result
        assert "video-player" in result
        assert "set-of-cards" in result
        assert "table" in result
        assert "chart-bar" in result
        assert "chart-line" in result
        assert "chart-pie" in result
        assert "chart-donut" in result
        assert "chart-mirrored-bar" in result

    def test_filtered_components(self):
        """Test that only allowed components are included."""
        allowed = {"one-card", "table"}
        result = build_components_description(allowed)
        assert "* one-card -" in result
        assert "* table -" in result
        assert "* image -" not in result
        assert "* chart-bar -" not in result

    def test_empty_set(self):
        """Test with empty set of allowed components."""
        result = build_components_description(set())
        assert result == ""

    def test_single_component(self):
        """Test with single component."""
        result = build_components_description({"image"})
        assert "* image -" in result
        assert "* one-card -" not in result


class TestBuildOnestepExamples:
    """Test build_onestep_examples function."""

    def test_all_examples_when_none(self):
        """Test that examples are included when allowed_components is None."""
        result = build_onestep_examples(None)
        assert "table" in result
        assert "one-card" in result
        assert "chart-bar" in result
        assert "chart-mirrored-bar" in result

    def test_filtered_examples(self):
        """Test that only allowed component examples are included."""
        allowed = {"table", "one-card"}
        result = build_onestep_examples(allowed)
        assert "table" in result
        assert "one-card" in result
        # chart examples should not be present
        assert "chart-bar" not in result or result.count("chart-bar") == 0

    def test_empty_set(self):
        """Test with empty set returns empty string."""
        result = build_onestep_examples(set())
        assert result == ""


class TestBuildTwostepStep1Examples:
    """Test build_twostep_step1_examples function."""

    def test_all_examples_when_none(self):
        """Test that examples are included when allowed_components is None."""
        result = build_twostep_step1_examples(None)
        assert "table" in result
        assert "one-card" in result
        assert "image" in result
        assert "chart-bar" in result
        assert "chart-mirrored-bar" in result

    def test_filtered_examples(self):
        """Test that only allowed component examples are included."""
        allowed = {"image"}
        result = build_twostep_step1_examples(allowed)
        assert "image" in result
        assert "table" not in result

    def test_empty_set(self):
        """Test with empty set returns empty string."""
        result = build_twostep_step1_examples(set())
        assert result == ""


class TestBuildTwostepStep2Example:
    """Test build_twostep_step2_example function."""

    def test_valid_component(self):
        """Test getting example for valid component."""
        result = build_twostep_step2_example("one-card")
        assert result
        assert "data_path" in result

    def test_chart_component(self):
        """Test getting example for chart component."""
        result = build_twostep_step2_example("chart-bar")
        assert result
        assert "data_path" in result

    def test_chart_alias(self):
        """Test that 'chart' alias works."""
        result = build_twostep_step2_example("chart")
        assert result
        # Should return chart-bar example as fallback
        assert "data_path" in result

    def test_invalid_component(self):
        """Test getting example for non-existent component."""
        result = build_twostep_step2_example("non-existent")
        assert result == ""


class TestBuildTwostepStep2Extension:
    """Test build_twostep_step2_extension function."""

    def test_component_with_extension(self):
        """Test getting extension for component that has one."""
        result = build_twostep_step2_extension("one-card")
        assert result
        assert "data_path" in result

    def test_component_without_extension(self):
        """Test getting extension for component without one."""
        result = build_twostep_step2_extension("table")
        # table doesn't have extension in metadata
        assert result == ""

    def test_chart_alias(self):
        """Test that 'chart' alias returns combined chart extensions."""
        result = build_twostep_step2_extension("chart")
        assert result
        assert "FIELDS:" in result

    def test_invalid_component(self):
        """Test getting extension for non-existent component."""
        result = build_twostep_step2_extension("non-existent")
        assert result == ""


class TestBuildChartInstructions:
    """Test build_chart_instructions function."""

    def test_empty_set(self):
        """Test that empty set returns empty string."""
        result = build_chart_instructions(set())
        assert result == ""

    def test_all_chart_types(self):
        """Test with all chart components."""
        result = build_chart_instructions(CHART_COMPONENTS)
        assert "CHART TYPES" in result
        assert "FIELDS BY TYPE" in result
        assert "RULES" in result
        assert "EXAMPLES" in result
        assert "chart-bar" in result
        assert "chart-line" in result
        assert "chart-pie" in result
        assert "chart-donut" in result
        assert "chart-mirrored-bar" in result

    def test_single_chart_type(self):
        """Test with single chart type."""
        result = build_chart_instructions({"chart-bar"})
        assert "CHART TYPES" in result
        assert "chart-bar" in result
        assert "chart-line" not in result
        assert "chart-pie" not in result

    def test_subset_of_charts(self):
        """Test with subset of chart types."""
        allowed = {"chart-bar", "chart-line"}
        result = build_chart_instructions(allowed)
        assert "chart-bar" in result
        assert "chart-line" in result
        assert "chart-pie" not in result
        assert "chart-donut" not in result
        assert "chart-mirrored-bar" not in result

    def test_common_rules_included(self):
        """Test that common rules are always included when charts are present."""
        result = build_chart_instructions({"chart-bar"})
        assert "Don't add unrequested metrics" in result

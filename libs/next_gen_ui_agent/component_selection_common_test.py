from next_gen_ui_agent.component_selection_common import (
    ALL_COMPONENTS,
    CHART_COMPONENTS,
    COMPONENT_METADATA,
    build_chart_instructions,
    build_components_description,
    build_twostep_step2configure_example,
    build_twostep_step2configure_rules,
    has_chart_components,
    has_non_chart_components,
    normalize_allowed_components,
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
            "twostep_step2configure_example",
        }

        for component, metadata in COMPONENT_METADATA.items():
            for field in required_fields:
                assert (
                    hasattr(metadata, field) and getattr(metadata, field) is not None
                ), f"Component {component} missing required field {field}"
                assert getattr(
                    metadata, field
                ), f"Component {component} has empty {field}"

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
                assert hasattr(
                    COMPONENT_METADATA[chart_comp], field
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


class TestNormalizeAllowedComponents:
    """Test normalize_allowed_components function."""

    def test_none_returns_all_components(self):
        """Test that None returns all components from COMPONENT_METADATA."""
        result = normalize_allowed_components(None, COMPONENT_METADATA)
        expected = set(COMPONENT_METADATA.keys())
        assert result == expected
        assert len(result) == 10  # All 10 components

    def test_valid_set_returns_same_set(self):
        """Test that a valid set is returned unchanged."""
        allowed = {"one-card", "table", "chart-bar"}
        result = normalize_allowed_components(allowed, COMPONENT_METADATA)
        assert result == {"one-card", "table", "chart-bar"}
        assert result is allowed  # Should return the same object

    def test_empty_set_returns_empty_set(self):
        """Test that empty set is returned unchanged."""
        allowed = set()
        result = normalize_allowed_components(allowed, COMPONENT_METADATA)
        assert result == set()
        assert len(result) == 0

    def test_single_component(self):
        """Test with single component."""
        allowed = {"image"}
        result = normalize_allowed_components(allowed, COMPONENT_METADATA)
        assert result == {"image"}

    def test_chart_components_only(self):
        """Test with only chart components."""
        allowed = CHART_COMPONENTS.copy()
        result = normalize_allowed_components(allowed, COMPONENT_METADATA)
        assert result == allowed
        assert len(result) == 5


class TestHasChartComponents:
    """Test has_chart_components function."""

    def test_with_chart_components(self):
        """Test that returns True when chart components are present."""
        allowed = {"table", "chart-bar", "one-card"}
        assert has_chart_components(allowed) is True

    def test_with_only_chart_components(self):
        """Test that returns True when only chart components are present."""
        allowed = {"chart-bar", "chart-line"}
        assert has_chart_components(allowed) is True

    def test_without_chart_components(self):
        """Test that returns False when no chart components are present."""
        allowed = {"table", "one-card", "set-of-cards"}
        assert has_chart_components(allowed) is False

    def test_with_empty_set(self):
        """Test that returns False with empty set."""
        allowed = set()
        assert has_chart_components(allowed) is False


class TestHasNonChartComponents:
    """Test has_non_chart_components function."""

    def test_with_non_chart_components(self):
        """Test that returns True when non-chart components are present."""
        allowed = {"table", "chart-bar", "one-card"}
        assert has_non_chart_components(allowed) is True

    def test_with_only_non_chart_components(self):
        """Test that returns True when only non-chart components are present."""
        allowed = {"table", "one-card", "set-of-cards"}
        assert has_non_chart_components(allowed) is True

    def test_with_only_chart_components(self):
        """Test that returns False when only chart components are present."""
        allowed = {"chart-bar", "chart-line", "chart-pie"}
        assert has_non_chart_components(allowed) is False

    def test_with_empty_set(self):
        """Test that returns False with empty set."""
        allowed = set()
        assert has_non_chart_components(allowed) is False


class TestBuildComponentsDescription:
    """Test build_components_description function."""

    def test_all_components(self):
        """Test with all components."""
        allowed = set(COMPONENT_METADATA.keys())
        result = build_components_description(allowed, COMPONENT_METADATA)
        # All components should be included
        for component in ALL_COMPONENTS:
            assert f"* {component} -" in result

    def test_filtered_components(self):
        """Test that only allowed components are included."""
        allowed = {"one-card", "table"}
        result = build_components_description(allowed, COMPONENT_METADATA)
        assert "* one-card -" in result
        assert "* table -" in result
        assert "* image -" not in result
        assert "* chart-bar -" not in result

    def test_empty_set(self):
        """Test with empty set of allowed components."""
        result = build_components_description(set(), COMPONENT_METADATA)
        assert result == ""

    def test_single_component(self):
        """Test with single component."""
        result = build_components_description({"image"}, COMPONENT_METADATA)
        assert "* image -" in result
        assert "* one-card -" not in result


class TestBuildTwostepStep2configureExample:
    """Test build_twostep_step2configure_example function."""

    def test_valid_component(self):
        """Test getting example for valid component."""
        result = build_twostep_step2configure_example("one-card", COMPONENT_METADATA)
        assert result
        assert "data_path" in result

    def test_chart_component(self):
        """Test getting example for chart component."""
        result = build_twostep_step2configure_example("chart-bar", COMPONENT_METADATA)
        assert result
        assert "data_path" in result

    def test_invalid_component(self):
        """Test getting example for non-existent component."""
        result = build_twostep_step2configure_example(
            "non-existent", COMPONENT_METADATA
        )
        assert result == ""


class TestBuildTwostepStep2configureRules:
    """Test build_twostep_step2configure_rules function."""

    def test_component_with_extension(self):
        """Test getting extension for component that has one."""
        result = build_twostep_step2configure_rules("one-card", COMPONENT_METADATA)
        assert result
        assert "data_path" in result

    def test_component_without_extension(self):
        """Test getting extension for component without one."""
        result = build_twostep_step2configure_rules("table", COMPONENT_METADATA)
        # table doesn't have extension in metadata
        assert result == ""

    def test_invalid_component(self):
        """Test getting extension for non-existent component."""
        result = build_twostep_step2configure_rules("non-existent", COMPONENT_METADATA)
        assert result == ""


class TestBuildChartInstructions:
    """Test build_chart_instructions function."""

    def test_empty_set(self):
        """Test that empty set returns empty string."""
        result = build_chart_instructions(set(), COMPONENT_METADATA)
        assert result == ""

    def test_all_chart_types(self):
        """Test with all chart components."""
        result = build_chart_instructions(CHART_COMPONENTS, COMPONENT_METADATA)
        assert "CHART TYPES" in result
        assert "FIELDS BY CHART TYPE" in result
        assert "CHART RULES" in result
        assert "CHART EXAMPLES" in result
        assert "chart-bar" in result
        assert "chart-line" in result
        assert "chart-pie" in result
        assert "chart-donut" in result
        assert "chart-mirrored-bar" in result

    def test_single_chart_type(self):
        """Test with single chart type."""
        result = build_chart_instructions({"chart-bar"}, COMPONENT_METADATA)
        assert "CHART TYPES" in result
        assert "chart-bar" in result
        assert "chart-line" not in result
        assert "chart-pie" not in result

    def test_subset_of_charts(self):
        """Test with subset of chart types."""
        allowed = {"chart-bar", "chart-line"}
        result = build_chart_instructions(allowed, COMPONENT_METADATA)
        assert "chart-bar" in result
        assert "chart-line" in result
        assert "chart-pie" not in result
        assert "chart-donut" not in result
        assert "chart-mirrored-bar" not in result

    def test_common_rules_included(self):
        """Test that common rules are always included when charts are present."""
        result = build_chart_instructions({"chart-bar"}, COMPONENT_METADATA)
        assert "Don't add unrequested metrics" in result

"""
Tests for main_args_handler module.
"""

import argparse
import os
from unittest.mock import patch

from next_gen_ui_mcp.main_args_handler import (
    get_sampling_cost_priority_configuration,
    get_sampling_hints_configuration,
    get_sampling_intelligence_priority_configuration,
    get_sampling_speed_priority_configuration,
)


class TestGetSamplingHintsConfiguration:
    """Tests for get_sampling_hints_configuration function."""

    def test_argument_takes_precedence_over_env(self) -> None:
        """Test that command-line argument takes precedence over environment variable."""
        args = argparse.Namespace(sampling_hints="claude-3-sonnet,claude")
        with patch.dict(os.environ, {"NGUI_SAMPLING_HINTS": "gpt-4,gpt-3.5"}):
            result = get_sampling_hints_configuration(args)
            assert result == ["claude-3-sonnet", "claude"]

    def test_env_var_used_when_arg_not_provided(self) -> None:
        """Test that environment variable is used when argument is not provided."""
        args = argparse.Namespace(sampling_hints=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_HINTS": "claude-3-sonnet,claude"}):
            result = get_sampling_hints_configuration(args)
            assert result == ["claude-3-sonnet", "claude"]

    def test_none_returned_when_neither_provided(self) -> None:
        """Test that None is returned when neither argument nor env var is provided."""
        args = argparse.Namespace(sampling_hints=None)
        with patch.dict(os.environ, {}, clear=True):
            result = get_sampling_hints_configuration(args)
            assert result is None

    def test_env_var_empty_string_returns_none(self) -> None:
        """Test that empty string in env var returns None."""
        args = argparse.Namespace(sampling_hints=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_HINTS": ""}):
            result = get_sampling_hints_configuration(args)
            assert result is None

    def test_env_var_whitespace_returns_none(self) -> None:
        """Test that whitespace-only env var returns None."""
        args = argparse.Namespace(sampling_hints=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_HINTS": "   "}):
            result = get_sampling_hints_configuration(args)
            assert result is None

    def test_single_hint(self) -> None:
        """Test that single hint is parsed correctly."""
        args = argparse.Namespace(sampling_hints="claude-3-sonnet")
        result = get_sampling_hints_configuration(args)
        assert result == ["claude-3-sonnet"]

    def test_multiple_hints_with_spaces(self) -> None:
        """Test that hints with spaces are trimmed correctly."""
        args = argparse.Namespace(sampling_hints="claude-3-sonnet, claude , gpt-4")
        result = get_sampling_hints_configuration(args)
        assert result == ["claude-3-sonnet", "claude", "gpt-4"]

    def test_empty_hints_filtered_out(self) -> None:
        """Test that empty hints after splitting are filtered out."""
        args = argparse.Namespace(sampling_hints="claude-3-sonnet,,claude,")
        result = get_sampling_hints_configuration(args)
        assert result == ["claude-3-sonnet", "claude"]


class TestGetSamplingCostPriorityConfiguration:
    """Tests for get_sampling_cost_priority_configuration function."""

    def test_argument_takes_precedence_over_env(self) -> None:
        """Test that command-line argument takes precedence over environment variable."""
        args = argparse.Namespace(sampling_cost_priority=0.8)
        with patch.dict(os.environ, {"NGUI_SAMPLING_COST_PRIORITY": "0.5"}):
            result = get_sampling_cost_priority_configuration(args)
            assert result == 0.8

    def test_env_var_used_when_arg_not_provided(self) -> None:
        """Test that environment variable is used when argument is not provided."""
        args = argparse.Namespace(sampling_cost_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_COST_PRIORITY": "0.7"}):
            result = get_sampling_cost_priority_configuration(args)
            assert result == 0.7

    def test_none_returned_when_neither_provided(self) -> None:
        """Test that None is returned when neither argument nor env var is provided."""
        args = argparse.Namespace(sampling_cost_priority=None)
        with patch.dict(os.environ, {}, clear=True):
            result = get_sampling_cost_priority_configuration(args)
            assert result is None

    def test_env_var_empty_string_returns_none(self) -> None:
        """Test that empty string in env var returns None."""
        args = argparse.Namespace(sampling_cost_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_COST_PRIORITY": ""}):
            result = get_sampling_cost_priority_configuration(args)
            assert result is None

    def test_env_var_whitespace_returns_none(self) -> None:
        """Test that whitespace-only env var returns None."""
        args = argparse.Namespace(sampling_cost_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_COST_PRIORITY": "   "}):
            result = get_sampling_cost_priority_configuration(args)
            assert result is None

    def test_float_conversion(self) -> None:
        """Test that env var string is converted to float."""
        args = argparse.Namespace(sampling_cost_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_COST_PRIORITY": "0.75"}):
            result = get_sampling_cost_priority_configuration(args)
            assert result == 0.75
            assert isinstance(result, float)


class TestGetSamplingSpeedPriorityConfiguration:
    """Tests for get_sampling_speed_priority_configuration function."""

    def test_argument_takes_precedence_over_env(self) -> None:
        """Test that command-line argument takes precedence over environment variable."""
        args = argparse.Namespace(sampling_speed_priority=0.9)
        with patch.dict(os.environ, {"NGUI_SAMPLING_SPEED_PRIORITY": "0.5"}):
            result = get_sampling_speed_priority_configuration(args)
            assert result == 0.9

    def test_env_var_used_when_arg_not_provided(self) -> None:
        """Test that environment variable is used when argument is not provided."""
        args = argparse.Namespace(sampling_speed_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_SPEED_PRIORITY": "0.6"}):
            result = get_sampling_speed_priority_configuration(args)
            assert result == 0.6

    def test_none_returned_when_neither_provided(self) -> None:
        """Test that None is returned when neither argument nor env var is provided."""
        args = argparse.Namespace(sampling_speed_priority=None)
        with patch.dict(os.environ, {}, clear=True):
            result = get_sampling_speed_priority_configuration(args)
            assert result is None

    def test_env_var_empty_string_returns_none(self) -> None:
        """Test that empty string in env var returns None."""
        args = argparse.Namespace(sampling_speed_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_SPEED_PRIORITY": ""}):
            result = get_sampling_speed_priority_configuration(args)
            assert result is None

    def test_env_var_whitespace_returns_none(self) -> None:
        """Test that whitespace-only env var returns None."""
        args = argparse.Namespace(sampling_speed_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_SPEED_PRIORITY": "   "}):
            result = get_sampling_speed_priority_configuration(args)
            assert result is None

    def test_float_conversion(self) -> None:
        """Test that env var string is converted to float."""
        args = argparse.Namespace(sampling_speed_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_SPEED_PRIORITY": "0.85"}):
            result = get_sampling_speed_priority_configuration(args)
            assert result == 0.85
            assert isinstance(result, float)


class TestGetSamplingIntelligencePriorityConfiguration:
    """Tests for get_sampling_intelligence_priority_configuration function."""

    def test_argument_takes_precedence_over_env(self) -> None:
        """Test that command-line argument takes precedence over environment variable."""
        args = argparse.Namespace(sampling_intelligence_priority=0.95)
        with patch.dict(os.environ, {"NGUI_SAMPLING_INTELLIGENCE_PRIORITY": "0.5"}):
            result = get_sampling_intelligence_priority_configuration(args)
            assert result == 0.95

    def test_env_var_used_when_arg_not_provided(self) -> None:
        """Test that environment variable is used when argument is not provided."""
        args = argparse.Namespace(sampling_intelligence_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_INTELLIGENCE_PRIORITY": "0.8"}):
            result = get_sampling_intelligence_priority_configuration(args)
            assert result == 0.8

    def test_none_returned_when_neither_provided(self) -> None:
        """Test that None is returned when neither argument nor env var is provided."""
        args = argparse.Namespace(sampling_intelligence_priority=None)
        with patch.dict(os.environ, {}, clear=True):
            result = get_sampling_intelligence_priority_configuration(args)
            assert result is None

    def test_env_var_empty_string_returns_none(self) -> None:
        """Test that empty string in env var returns None."""
        args = argparse.Namespace(sampling_intelligence_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_INTELLIGENCE_PRIORITY": ""}):
            result = get_sampling_intelligence_priority_configuration(args)
            assert result is None

    def test_env_var_whitespace_returns_none(self) -> None:
        """Test that whitespace-only env var returns None."""
        args = argparse.Namespace(sampling_intelligence_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_INTELLIGENCE_PRIORITY": "   "}):
            result = get_sampling_intelligence_priority_configuration(args)
            assert result is None

    def test_float_conversion(self) -> None:
        """Test that env var string is converted to float."""
        args = argparse.Namespace(sampling_intelligence_priority=None)
        with patch.dict(os.environ, {"NGUI_SAMPLING_INTELLIGENCE_PRIORITY": "0.92"}):
            result = get_sampling_intelligence_priority_configuration(args)
            assert result == 0.92
            assert isinstance(result, float)

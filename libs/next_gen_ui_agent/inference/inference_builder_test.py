"""
Tests for inference_builder module, focusing on argument precedence over environment variables.
"""

import argparse
import logging
import os
from unittest.mock import MagicMock, patch

import pytest
from next_gen_ui_agent.inference.inference_builder import (
    add_inference_comandline_args,
    create_inference_from_arguments,
    get_sampling_max_tokens_configuration,
)


class TestGetSamplingMaxTokensConfiguration:
    """Tests for get_sampling_max_tokens_configuration function."""

    def test_argument_takes_precedence_over_env(self) -> None:
        """Test that command-line argument takes precedence over environment variable."""
        args = argparse.Namespace(sampling_max_tokens=2048)
        with patch.dict(os.environ, {"NGUI_PROVIDER_SAMPLING_MAX_TOKENS": "1024"}):
            result = get_sampling_max_tokens_configuration(args, 4096)
            assert result == 2048

    def test_env_var_used_when_arg_not_provided(self) -> None:
        """Test that environment variable is used when argument is not provided."""
        args = argparse.Namespace(sampling_max_tokens=None)
        with patch.dict(os.environ, {"NGUI_PROVIDER_SAMPLING_MAX_TOKENS": "1024"}):
            result = get_sampling_max_tokens_configuration(args, 4096)
            assert result == 1024

    def test_default_used_when_neither_provided(self) -> None:
        """Test that default value is used when neither argument nor env var is provided."""
        args = argparse.Namespace(sampling_max_tokens=None)
        with patch.dict(os.environ, {}, clear=True):
            result = get_sampling_max_tokens_configuration(args, 4096)
            assert result == 4096

    def test_env_var_empty_string_uses_default(self) -> None:
        """Test that empty string in env var uses default."""
        args = argparse.Namespace(sampling_max_tokens=None)
        with patch.dict(os.environ, {"NGUI_PROVIDER_SAMPLING_MAX_TOKENS": ""}):
            result = get_sampling_max_tokens_configuration(args, 4096)
            assert result == 4096

    def test_env_var_whitespace_uses_default(self) -> None:
        """Test that whitespace-only env var uses default."""
        args = argparse.Namespace(sampling_max_tokens=None)
        with patch.dict(os.environ, {"NGUI_PROVIDER_SAMPLING_MAX_TOKENS": "   "}):
            result = get_sampling_max_tokens_configuration(args, 4096)
            assert result == 4096


class TestCreateInferenceFromArguments:
    """Tests for create_inference_from_arguments function."""

    @pytest.fixture
    def logger(self) -> logging.Logger:
        """Create a logger for testing."""
        return logging.getLogger("test")

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create an ArgumentParser with inference arguments."""
        parser = argparse.ArgumentParser()
        add_inference_comandline_args(parser, default_provider="openai")
        return parser

    def test_provider_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --provider argument takes precedence over NGUI_PROVIDER env var."""
        with patch.dict(os.environ, {"NGUI_PROVIDER": "anthropic-vertexai"}):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai", "--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                result = create_inference_from_arguments(parser, args, logger)
                assert result == mock_inference
                # Verify it was called with OpenAI settings, not anthropic
                mock_create.assert_called_once()
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["model"] == "gpt-4"

    def test_provider_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_PROVIDER env var is used when --provider argument is not provided."""
        with patch.dict(os.environ, {"NGUI_PROVIDER": "openai"}):
            parser = self._create_parser()
            args = parser.parse_args(["--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                result = create_inference_from_arguments(parser, args, logger)
                assert result == mock_inference
                mock_create.assert_called_once()

    def test_provider_default_used_when_neither_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that default provider is used when neither argument nor env var is provided."""
        with patch.dict(os.environ, {}, clear=True):
            parser = self._create_parser()
            args = parser.parse_args(["--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                result = create_inference_from_arguments(parser, args, logger)
                assert result == mock_inference
                mock_create.assert_called_once()

    def test_model_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --model argument takes precedence over NGUI_MODEL env var."""
        with patch.dict(os.environ, {"NGUI_MODEL": "gpt-3.5-turbo"}):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai", "--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["model"] == "gpt-4"

    def test_model_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_MODEL env var is used when --model argument is not provided."""
        with patch.dict(os.environ, {"NGUI_MODEL": "gpt-3.5-turbo"}):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["model"] == "gpt-3.5-turbo"

    def test_base_url_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --base-url argument takes precedence over NGUI_PROVIDER_API_BASE_URL env var."""
        with patch.dict(
            os.environ, {"NGUI_PROVIDER_API_BASE_URL": "http://env-url.com"}
        ):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "openai",
                    "--model",
                    "gpt-4",
                    "--base-url",
                    "http://custom-url.com",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["base_url"] == "http://custom-url.com"

    def test_base_url_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_PROVIDER_API_BASE_URL env var is used when --base-url argument is not provided."""
        with patch.dict(
            os.environ, {"NGUI_PROVIDER_API_BASE_URL": "http://env-url.com"}
        ):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai", "--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["base_url"] == "http://env-url.com"

    def test_api_key_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --api-key argument takes precedence over NGUI_PROVIDER_API_KEY env var."""
        with patch.dict(os.environ, {"NGUI_PROVIDER_API_KEY": "env-key-456"}):
            parser = self._create_parser()
            args = parser.parse_args(
                ["--provider", "openai", "--model", "gpt-4", "--api-key", "arg-key-123"]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["api_key"] == "arg-key-123"

    def test_api_key_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_PROVIDER_API_KEY env var is used when --api-key argument is not provided."""
        with patch.dict(os.environ, {"NGUI_PROVIDER_API_KEY": "env-key-456"}):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai", "--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["api_key"] == "env-key-456"

    def test_temperature_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --temperature argument takes precedence over NGUI_PROVIDER_TEMPERATURE env var."""
        with patch.dict(os.environ, {"NGUI_PROVIDER_TEMPERATURE": "0.5"}):
            parser = self._create_parser()
            args = parser.parse_args(
                ["--provider", "openai", "--model", "gpt-4", "--temperature", "0.7"]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["temperature"] == 0.7

    def test_temperature_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_PROVIDER_TEMPERATURE env var is used when --temperature argument is not provided."""
        with patch.dict(os.environ, {"NGUI_PROVIDER_TEMPERATURE": "0.5"}):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai", "--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["temperature"] == 0.5

    def test_temperature_default_when_neither_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that default temperature (0.0) is used when neither argument nor env var is provided."""
        with patch.dict(os.environ, {}, clear=True):
            parser = self._create_parser()
            args = parser.parse_args(["--provider", "openai", "--model", "gpt-4"])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["temperature"] == 0.0

    def test_anthropic_version_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --anthropic-version argument takes precedence over NGUI_PROVIDER_ANTHROPIC_VERSION env var."""
        with patch.dict(
            os.environ, {"NGUI_PROVIDER_ANTHROPIC_VERSION": "vertex-2023-10-16"}
        ):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "anthropic-vertexai",
                    "--model",
                    "claude-3",
                    "--base-url",
                    "http://vertex-ai.com",
                    "--anthropic-version",
                    "vertex-2024-01-01",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.ProxiedAnthropicVertexAIInference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["anthropic_version"] == "vertex-2024-01-01"

    def test_anthropic_version_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_PROVIDER_ANTHROPIC_VERSION env var is used when --anthropic-version argument is not provided."""
        with patch.dict(
            os.environ, {"NGUI_PROVIDER_ANTHROPIC_VERSION": "vertex-2024-01-01"}
        ):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "anthropic-vertexai",
                    "--model",
                    "claude-3",
                    "--base-url",
                    "http://vertex-ai.com",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.ProxiedAnthropicVertexAIInference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["anthropic_version"] == "vertex-2024-01-01"

    def test_anthropic_version_default_when_neither_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that default anthropic version is used when neither argument nor env var is provided."""
        with patch.dict(os.environ, {}, clear=True):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "anthropic-vertexai",
                    "--model",
                    "claude-3",
                    "--base-url",
                    "http://vertex-ai.com",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.ProxiedAnthropicVertexAIInference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["anthropic_version"] == "vertex-2023-10-16"

    def test_sampling_max_tokens_argument_takes_precedence_over_env(
        self, logger: logging.Logger
    ) -> None:
        """Test that --sampling-max-tokens argument takes precedence over NGUI_SAMPLING_MAX_TOKENS env var."""
        with patch.dict(os.environ, {"NGUI_SAMPLING_MAX_TOKENS": "1024"}):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "anthropic-vertexai",
                    "--model",
                    "claude-3",
                    "--base-url",
                    "http://vertex-ai.com",
                    "--sampling-max-tokens",
                    "2048",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.ProxiedAnthropicVertexAIInference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["max_tokens"] == 2048

    def test_sampling_max_tokens_env_var_used_when_arg_not_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that NGUI_SAMPLING_MAX_TOKENS env var is used when --sampling-max-tokens argument is not provided."""
        with patch.dict(os.environ, {"NGUI_SAMPLING_MAX_TOKENS": "1024"}):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "anthropic-vertexai",
                    "--model",
                    "claude-3",
                    "--base-url",
                    "http://vertex-ai.com",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.ProxiedAnthropicVertexAIInference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["max_tokens"] == 1024

    def test_sampling_max_tokens_default_when_neither_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that default max_tokens (4096) is used when neither argument nor env var is provided."""
        with patch.dict(os.environ, {}, clear=True):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "anthropic-vertexai",
                    "--model",
                    "claude-3",
                    "--base-url",
                    "http://vertex-ai.com",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.ProxiedAnthropicVertexAIInference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["max_tokens"] == 4096

    def test_all_arguments_take_precedence_over_all_env_vars(
        self, logger: logging.Logger
    ) -> None:
        """Test that all arguments take precedence over all corresponding environment variables."""
        env_vars = {
            "NGUI_PROVIDER": "anthropic-vertexai",
            "NGUI_MODEL": "gpt-3.5-turbo",
            "NGUI_PROVIDER_API_BASE_URL": "http://env-url.com",
            "NGUI_PROVIDER_API_KEY": "env-key",
            "NGUI_PROVIDER_TEMPERATURE": "0.3",
        }
        with patch.dict(os.environ, env_vars):
            parser = self._create_parser()
            args = parser.parse_args(
                [
                    "--provider",
                    "openai",
                    "--model",
                    "gpt-4",
                    "--base-url",
                    "http://arg-url.com",
                    "--api-key",
                    "arg-key",
                    "--temperature",
                    "0.8",
                ]
            )
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["model"] == "gpt-4"
                assert call_kwargs["base_url"] == "http://arg-url.com"
                assert call_kwargs["api_key"] == "arg-key"
                assert call_kwargs["temperature"] == 0.8

    def test_all_env_vars_used_when_no_arguments_provided(
        self, logger: logging.Logger
    ) -> None:
        """Test that all environment variables are used when no arguments are provided."""
        env_vars = {
            "NGUI_PROVIDER": "openai",
            "NGUI_MODEL": "gpt-3.5-turbo",
            "NGUI_PROVIDER_API_BASE_URL": "http://env-url.com",
            "NGUI_PROVIDER_API_KEY": "env-key",
            "NGUI_PROVIDER_TEMPERATURE": "0.3",
        }
        with patch.dict(os.environ, env_vars):
            parser = self._create_parser()
            args = parser.parse_args([])
            with patch(
                "next_gen_ui_agent.inference.inference_builder.create_langchain_openai_inference"
            ) as mock_create:
                mock_inference = MagicMock()
                mock_create.return_value = mock_inference
                create_inference_from_arguments(parser, args, logger)
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["model"] == "gpt-3.5-turbo"
                assert call_kwargs["base_url"] == "http://env-url.com"
                assert call_kwargs["api_key"] == "env-key"
                assert call_kwargs["temperature"] == 0.3

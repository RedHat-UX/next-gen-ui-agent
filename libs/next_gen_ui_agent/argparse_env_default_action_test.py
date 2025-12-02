import argparse
import os

import pytest
from next_gen_ui_agent.argparse_env_default_action import EnvDefault


class TestEnvDefault:
    """Tests for EnvDefault argparse action."""

    def test_env_var_used_as_default_when_arg_not_provided(self):
        """Test that environment variable is used as default when argument is not provided."""
        env_var = "TEST_URL"
        env_value = "http://example.com"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                help="Test URL argument",
            )

            args = parser.parse_args([])
            assert args.url == env_value
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_command_line_arg_overrides_env_var(self):
        """Test that command line argument overrides environment variable."""
        env_var = "TEST_URL"
        env_value = "http://env.example.com"
        cli_value = "http://cli.example.com"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                help="Test URL argument",
            )

            args = parser.parse_args(["--url", cli_value])
            assert args.url == cli_value
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_empty_env_var_not_used_as_default(self):
        """Test that empty environment variable is not used as default."""
        env_var = "TEST_URL"

        # Set empty environment variable
        os.environ[env_var] = ""

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                default="default_value",
                help="Test URL argument",
            )

            args = parser.parse_args([])
            assert args.url == "default_value"
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_whitespace_only_env_var_not_used_as_default(self):
        """Test that whitespace-only environment variable is not used as default."""
        env_var = "TEST_URL"

        # Set whitespace-only environment variable
        os.environ[env_var] = "   \t\n  "

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                default="default_value",
                help="Test URL argument",
            )

            args = parser.parse_args([])
            assert args.url == "default_value"
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_required_true_with_env_var_sets_required_false(self):
        """Test that required=True with env var set makes required=False."""
        env_var = "TEST_URL"
        env_value = "http://example.com"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                required=True,
                help="Test URL argument",
            )

            # Should not raise SystemExit because required is now False
            args = parser.parse_args([])
            assert args.url == env_value
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_required_true_without_env_var_remains_required(self):
        """Test that required=True without env var remains required=True."""
        env_var = "TEST_URL"

        # Ensure environment variable is not set
        if env_var in os.environ:
            del os.environ[env_var]

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-u",
            "--url",
            action=EnvDefault,
            envvar=env_var,
            required=True,
            help="Test URL argument",
        )

        # Should raise SystemExit because argument is required and not provided
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_default_value_when_env_var_not_set(self):
        """Test that default value is used when environment variable is not set."""
        env_var = "TEST_URL"
        default_value = "http://default.example.com"

        # Ensure environment variable is not set
        if env_var in os.environ:
            del os.environ[env_var]

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-u",
            "--url",
            action=EnvDefault,
            envvar=env_var,
            default=default_value,
            help="Test URL argument",
        )

        args = parser.parse_args([])
        assert args.url == default_value

    def test_multiple_args_with_different_env_vars(self):
        """Test multiple arguments with different environment variables."""
        env_var1 = "TEST_URL"
        env_var2 = "TEST_PORT"
        env_value1 = "http://example.com"
        env_value2 = "8080"

        # Set environment variables
        os.environ[env_var1] = env_value1
        os.environ[env_var2] = env_value2

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var1,
                help="Test URL argument",
            )
            parser.add_argument(
                "-p",
                "--port",
                action=EnvDefault,
                envvar=env_var2,
                help="Test port argument",
            )

            args = parser.parse_args([])
            assert args.url == env_value1
            assert args.port == env_value2
        finally:
            # Clean up
            if env_var1 in os.environ:
                del os.environ[env_var1]
            if env_var2 in os.environ:
                del os.environ[env_var2]

    def test_env_var_with_whitespace_trimmed(self):
        """Test that environment variable value with leading/trailing whitespace is used."""
        env_var = "TEST_URL"
        env_value = "  http://example.com  "

        # Set environment variable with whitespace
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                help="Test URL argument",
            )

            # The implementation checks if stripped value is not empty,
            # but uses the original value (not stripped) as default
            args = parser.parse_args([])
            assert args.url == env_value
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_no_envvar_parameter(self):
        """Test behavior when envvar is None or empty."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-u",
            "--url",
            action=EnvDefault,
            envvar=None,
            default="default_value",
            help="Test URL argument",
        )

        args = parser.parse_args([])
        assert args.url == "default_value"

    def test_required_false_with_env_var(self):
        """Test that required=False works correctly with env var."""
        env_var = "TEST_URL"
        env_value = "http://example.com"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-u",
                "--url",
                action=EnvDefault,
                envvar=env_var,
                required=False,
                help="Test URL argument",
            )

            args = parser.parse_args([])
            assert args.url == env_value
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_int_type_with_env_var(self):
        """Test that environment variable is converted to int when type=int."""
        env_var = "TEST_PORT"
        env_value = "8080"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-p",
                "--port",
                action=EnvDefault,
                envvar=env_var,
                type=int,
                help="Test port argument",
            )

            args = parser.parse_args([])
            assert args.port == 8080
            assert isinstance(args.port, int)
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_int_type_command_line_overrides_env_var(self):
        """Test that command line argument with int type overrides environment variable."""
        env_var = "TEST_PORT"
        env_value = "8080"
        cli_value = "9090"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-p",
                "--port",
                action=EnvDefault,
                envvar=env_var,
                type=int,
                help="Test port argument",
            )

            args = parser.parse_args(["--port", cli_value])
            assert args.port == 9090
            assert isinstance(args.port, int)
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_int_type_default_value_when_env_var_not_set(self):
        """Test that default int value is used when environment variable is not set."""
        env_var = "TEST_PORT"
        default_value = 3000

        # Ensure environment variable is not set
        if env_var in os.environ:
            del os.environ[env_var]

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-p",
            "--port",
            action=EnvDefault,
            envvar=env_var,
            type=int,
            default=default_value,
            help="Test port argument",
        )

        args = parser.parse_args([])
        assert args.port == default_value
        assert isinstance(args.port, int)

    def test_int_type_required_with_env_var(self):
        """Test that required=True with int type and env var set makes required=False."""
        env_var = "TEST_PORT"
        env_value = "8080"

        # Set environment variable
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-p",
                "--port",
                action=EnvDefault,
                envvar=env_var,
                type=int,
                required=True,
                help="Test port argument",
            )

            # Should not raise SystemExit because required is now False
            args = parser.parse_args([])
            assert args.port == 8080
            assert isinstance(args.port, int)
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

    def test_int_type_invalid_env_var_raises_error(self):
        """Test that invalid integer in environment variable raises error."""
        env_var = "TEST_PORT"
        env_value = "not_an_integer"

        # Set environment variable with invalid integer
        os.environ[env_var] = env_value

        try:
            parser = argparse.ArgumentParser()
            parser.add_argument(
                "-p",
                "--port",
                action=EnvDefault,
                envvar=env_var,
                type=int,
                help="Test port argument",
            )

            # Should raise SystemExit because argparse cannot convert to int
            with pytest.raises(SystemExit):
                parser.parse_args([])
        finally:
            # Clean up
            if env_var in os.environ:
                del os.environ[env_var]

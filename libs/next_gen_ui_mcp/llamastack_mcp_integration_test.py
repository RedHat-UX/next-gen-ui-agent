#!/usr/bin/env python3
"""
Integration test for Llama Stack with NextGenUI MCP server.

This test demonstrates and validates:
1. Starting Llama Stack as an embedded library using AsyncLlamaStackAsLibraryClient
2. Registering the NextGenUI MCP server with Llama Stack
3. Testing the MCP tool integration through Llama Stack

The NextGenUI MCP agent uses MCP sampling protocol for LLM inference, allowing it to
leverage the connected client's LLM capabilities through the MCP sampling interface.

Usage:
    # Run as pytest
    pytest libs/next_gen_ui_mcp/llamastack_mcp_integration_test.py -v

    # Run as pytest with debug logging
    pytest libs/next_gen_ui_mcp/llamastack_mcp_integration_test.py -v -s --log-cli-level=DEBUG

The test will:
- Initialize Llama Stack as a library
- Register the NextGenUI MCP server (assumes server_example.py is available)
- Create an MCP agent that uses sampling for LLM inference
- Test the MCP tool integration
- Clean up resources
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import pytest if available
try:
    import pytest

    PYTEST_AVAILABLE = True
    pytest_plugins: list[str] = []
except ImportError:
    PYTEST_AVAILABLE = False

    # Create a dummy pytest module for when running directly
    class DummyPytest:
        class mark:
            @staticmethod
            def skipif(condition, *, reason):
                def decorator(func):
                    if condition:

                        def wrapper(*args, **kwargs):
                            print(f"SKIPPED: {reason}")
                            return

                        return wrapper
                    return func

                return decorator

            @staticmethod
            def asyncio(func):
                return func

    pytest = DummyPytest()

try:
    from llama_stack.distribution.library_client import AsyncLlamaStackAsLibraryClient

    # ToolRuntimeConfig may not be available in current version
    try:
        from llama_stack_client.types.tool_runtime import ToolRuntimeConfig
    except ImportError:
        # Create a dummy type for compatibility
        ToolRuntimeConfig = dict

    LLAMA_STACK_AVAILABLE = True
except ImportError as e:
    LLAMA_STACK_AVAILABLE = False
    SKIP_REASON = f"Llama Stack dependencies not found: {e}. Install with: pip install llama-stack-client>=0.1.9,<=0.2.15"

try:
    from next_gen_ui_mcp.agent import NextGenUIMCPAgent

    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    if LLAMA_STACK_AVAILABLE:
        SKIP_REASON = (
            f"MCP dependencies not found: {e}. Install with: pip install mcp>=1.12.0"
        )
    NextGenUIMCPAgent = None  # type: ignore

logger = logging.getLogger(__name__)

# Test configuration
DEFAULT_CONFIG_FILE = "tests/ai_eval_components/llamastack-ollama.yaml"
DEFAULT_MODEL = "granite3.3:2b"
DEFAULT_MCP_SERVER_COMMAND = ["python", "libs/next_gen_ui_mcp/server_example.py"]

# Test data
TEST_INPUT_DATA = {
    "user_prompt": "Show movie details",
    "input_data": [
        {
            "id": "movie1",
            "data": '{"title": "Inception", "year": 2010, "director": "Christopher Nolan", "rating": 8.8}',
        }
    ],
}


class LlamaStackMCPTestManager:
    """Test manager for Llama Stack with MCP server integration."""

    def __init__(
        self,
        config_file: str = DEFAULT_CONFIG_FILE,
        model: str = DEFAULT_MODEL,
        mcp_server_command: Optional[list[str]] = None,
    ):
        self.config_file = config_file
        self.model = model
        self.mcp_server_command = mcp_server_command or DEFAULT_MCP_SERVER_COMMAND
        self.llama_client: Optional[AsyncLlamaStackAsLibraryClient] = None
        self.mcp_agent: Optional[NextGenUIMCPAgent] = None

    async def initialize_llama_stack(self) -> None:
        """Initialize Llama Stack as a library."""
        logger.info("Initializing Llama Stack with config: %s", self.config_file)
        logger.info("Using model: %s", self.model)

        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Llama Stack config file not found: {self.config_file}"
            )

        self.llama_client = AsyncLlamaStackAsLibraryClient(self.config_file)
        await self.llama_client.initialize()

        logger.info("Llama Stack initialized successfully")

    async def register_mcp_server(self) -> None:
        """Register the NextGenUI MCP server with Llama Stack."""
        if not self.llama_client:
            raise RuntimeError("Llama Stack client not initialized")

        logger.info("Registering NextGenUI MCP server...")
        logger.info("MCP server command: %s", " ".join(self.mcp_server_command))

        try:
            # Register the MCP server as a tool runtime
            tool_runtime_config = ToolRuntimeConfig(
                tool_runtime_type="mcp",
                config={
                    "command": self.mcp_server_command,
                    "env": {},  # Add any environment variables if needed
                },
            )

            # Register the tool runtime with Llama Stack
            await self.llama_client.tool_runtime.register_tool_runtime(
                tool_runtime_id="nextgen_ui_mcp",
                tool_runtime_config=tool_runtime_config,
            )

            logger.info("NextGenUI MCP server registered successfully")

        except Exception as e:
            logger.exception("Failed to register MCP server: %s", e)
            raise

    async def create_mcp_agent(self) -> None:
        """Create NextGenUI MCP agent for testing purposes."""
        if not self.llama_client:
            raise RuntimeError("Llama Stack client not initialized")

        logger.info("Creating NextGenUI MCP agent for testing...")

        # Create MCP agent (no inference parameter needed - uses MCP sampling)
        # The agent will use sampling through the MCP protocol when connected to clients
        self.mcp_agent = NextGenUIMCPAgent(
            component_system="json", name="NextGenUI-MCP-Server-Test"
        )

        logger.info("NextGenUI MCP agent created successfully")
        logger.info("Agent will use MCP sampling when called by clients")

    async def test_mcp_tool_integration(self) -> dict:
        """Test the MCP integration by calling the tool through Llama Stack."""
        if not self.llama_client:
            raise RuntimeError("Llama Stack client not available for testing")

        logger.info("Testing MCP tool integration...")

        # Allow some time for the MCP server to start up
        logger.info("Waiting for MCP server to be ready...")
        await asyncio.sleep(3)

        try:
            # Test calling the MCP tool through Llama Stack
            result = await self.llama_client.tool_runtime.invoke_tool(
                tool_name="generate_ui", kwargs=TEST_INPUT_DATA
            )

            logger.info("MCP tool test successful!")
            logger.info("Result: %s", result)
            if hasattr(result, "__dict__"):
                return dict(result)
            elif isinstance(result, dict):
                return result
            else:
                # Convert other types to dict format
                return {"result": result}

        except Exception as e:
            logger.exception("MCP tool test failed: %s", e)
            raise

    async def setup(self) -> None:
        """Set up the complete test environment."""
        await self.initialize_llama_stack()
        await self.register_mcp_server()
        await self.create_mcp_agent()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Cleaning up test resources...")
        if self.llama_client:
            # Add any cleanup logic if needed
            pass


@pytest.mark.skipif(not LLAMA_STACK_AVAILABLE or not MCP_AVAILABLE, reason=SKIP_REASON)
@pytest.mark.skipif(
    not os.path.exists(DEFAULT_CONFIG_FILE),
    reason=f"Llama Stack config file not found: {DEFAULT_CONFIG_FILE}",
)
@pytest.mark.asyncio
async def test_llamastack_mcp_integration():
    """
    Integration test for Llama Stack with NextGenUI MCP server.

    This test validates that:
    1. Llama Stack can be initialized as a library
    2. NextGenUI MCP server can be registered with Llama Stack
    3. The MCP tool can be successfully invoked through Llama Stack
    4. The returned result has the expected structure
    """
    manager = LlamaStackMCPTestManager()

    try:
        # Setup the test environment
        await manager.setup()

        # Test the MCP tool integration
        result = await manager.test_mcp_tool_integration()

        # Validate the result
        assert result is not None, "MCP tool should return a result"

        # The result should be a dictionary or list containing UI component data
        assert isinstance(
            result, (dict, list)
        ), f"Expected dict or list, got {type(result)}"

        if isinstance(result, dict):
            # If it's a single component, check for required fields
            assert (
                "id" in result or "content" in result
            ), "Result should contain component data"
        elif isinstance(result, list):
            # If it's a list of components, check that it's not empty
            assert len(result) > 0, "Result list should not be empty"

        logger.info("✅ Llama Stack MCP integration test passed!")

    except Exception as e:
        logger.exception("❌ Llama Stack MCP integration test failed: %s", e)
        raise
    finally:
        # Always clean up
        await manager.cleanup()


@pytest.mark.skipif(not LLAMA_STACK_AVAILABLE or not MCP_AVAILABLE, reason=SKIP_REASON)
@pytest.mark.skipif(
    not os.path.exists(DEFAULT_CONFIG_FILE),
    reason=f"Llama Stack config file not found: {DEFAULT_CONFIG_FILE}",
)
@pytest.mark.asyncio
async def test_llamastack_initialization():
    """
    Test that Llama Stack can be initialized properly.

    This is a lighter test that only validates Llama Stack initialization
    without requiring the MCP server to be running.
    """
    manager = LlamaStackMCPTestManager()

    try:
        # Test Llama Stack initialization
        await manager.initialize_llama_stack()

        # Validate that the client was created
        assert (
            manager.llama_client is not None
        ), "Llama Stack client should be initialized"

        logger.info("✅ Llama Stack initialization test passed!")

    except Exception as e:
        logger.exception("❌ Llama Stack initialization test failed: %s", e)
        raise
    finally:
        # Clean up
        await manager.cleanup()


@pytest.mark.skipif(not LLAMA_STACK_AVAILABLE or not MCP_AVAILABLE, reason=SKIP_REASON)
@pytest.mark.asyncio
async def test_mcp_agent_creation():
    """
    Test that NextGenUI MCP agent can be created properly.

    This test validates the MCP agent creation without requiring Llama Stack.
    """
    manager = LlamaStackMCPTestManager()

    try:
        # Create a mock llama client to satisfy the requirement
        manager.llama_client = "mock_client"  # Just to pass the check

        # Test MCP agent creation
        await manager.create_mcp_agent()

        # Validate that the agent was created
        assert manager.mcp_agent is not None, "MCP agent should be created"
        assert isinstance(
            manager.mcp_agent, NextGenUIMCPAgent
        ), "Should be NextGenUIMCPAgent instance"

        logger.info("✅ MCP agent creation test passed!")

    except Exception as e:
        logger.exception("❌ MCP agent creation test failed: %s", e)
        raise
    finally:
        # Clean up
        await manager.cleanup()


if __name__ == "__main__":
    """
    Allow running this test file directly for development and debugging.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Llama Stack MCP integration tests"
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG_FILE, help="Llama Stack config file"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    async def run_tests():
        """Run the tests manually."""
        logger.info("Running Llama Stack MCP integration tests...")

        if not LLAMA_STACK_AVAILABLE or not MCP_AVAILABLE:
            logger.error("Cannot run tests: %s", SKIP_REASON)
            return

        if not os.path.exists(args.config):
            logger.error("Config file not found: %s", args.config)
            return

        # Override defaults if provided
        global DEFAULT_CONFIG_FILE, DEFAULT_MODEL
        DEFAULT_CONFIG_FILE = args.config
        DEFAULT_MODEL = args.model

        try:
            await test_llamastack_initialization()
            await test_mcp_agent_creation()
            await test_llamastack_mcp_integration()
            logger.info("🎉 All tests passed!")
        except Exception as e:
            logger.exception("💥 Tests failed: %s", e)
            sys.exit(1)

    # Run the tests
    asyncio.run(run_tests())

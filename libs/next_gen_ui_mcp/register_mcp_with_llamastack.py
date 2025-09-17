#!/usr/bin/env python3
"""
Script to register NextGenUI MCP server with an existing Llama Stack instance.

This script is useful when you already have Llama Stack running and want to
register the NextGenUI MCP server as a tool runtime.

Usage:
    # Register with default Llama Stack URL
    python register_mcp_with_llamastack.py

    # Register with custom Llama Stack URL
    python register_mcp_with_llamastack.py --llama-url http://localhost:5001

    # Test the registration
    python register_mcp_with_llamastack.py --test

Prerequisites:
- Llama Stack server must be running
- NextGenUI MCP server (server_example.py) must be available to start
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from llama_stack_client import AsyncLlamaStackClient

    # ToolRuntimeConfig may not be available in current version
    try:
        from llama_stack_client.types.tool_runtime import ToolRuntimeConfig
    except ImportError:
        # Create a dummy type for compatibility
        ToolRuntimeConfig = dict
except ImportError as e:
    print(f"Error: Llama Stack dependencies not found: {e}")
    print("Please install with: pip install llama-stack-client>=0.1.9,<=0.2.15")
    sys.exit(1)

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_LLAMA_STACK_URL = "http://localhost:5001"
DEFAULT_MCP_SERVER_COMMAND = ["python", "libs/next_gen_ui_mcp/server_example.py"]


class MCPRegistrationManager:
    """Manager for registering MCP server with existing Llama Stack."""

    def __init__(
        self,
        llama_stack_url: str,
        mcp_server_command: Optional[list[str]] = None,
    ):
        self.llama_stack_url = llama_stack_url
        self.mcp_server_command = mcp_server_command or DEFAULT_MCP_SERVER_COMMAND
        self.client: Optional[AsyncLlamaStackClient] = None

    async def connect_to_llama_stack(self) -> None:
        """Connect to existing Llama Stack instance."""
        logger.info("Connecting to Llama Stack at: %s", self.llama_stack_url)

        self.client = AsyncLlamaStackClient(base_url=self.llama_stack_url)

        # Test the connection
        try:
            # Try to list models to verify connection
            models = await self.client.models.list()
            logger.info(
                "Connected successfully. Available models: %s",
                [getattr(m, "model_id", getattr(m, "id", str(m))) for m in models],
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Llama Stack at {self.llama_stack_url}: {e}"
            )

    async def register_mcp_server(self) -> None:
        """Register the NextGenUI MCP server with Llama Stack."""
        if not self.client:
            raise RuntimeError("Not connected to Llama Stack")

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
            # Check if the method exists and handle different API versions
            if hasattr(self.client.tool_runtime, "register_tool_runtime"):
                await self.client.tool_runtime.register_tool_runtime(
                    tool_runtime_id="nextgen_ui_mcp",
                    tool_runtime_config=tool_runtime_config,
                )
            elif hasattr(self.client.tool_runtime, "register"):
                await self.client.tool_runtime.register(
                    runtime_id="nextgen_ui_mcp",
                    config=tool_runtime_config,
                )
            else:
                raise RuntimeError(
                    "Llama Stack tool runtime registration method not found"
                )

            logger.info(
                "NextGenUI MCP server registered successfully with ID: nextgen_ui_mcp"
            )

        except Exception as e:
            logger.exception("Failed to register MCP server: %s", e)
            raise

    async def list_tool_runtimes(self) -> None:
        """List all registered tool runtimes."""
        if not self.client:
            raise RuntimeError("Not connected to Llama Stack")

        try:
            # Handle different API versions
            if hasattr(self.client.tool_runtime, "list_tool_runtimes"):
                runtimes = await self.client.tool_runtime.list_tool_runtimes()
            elif hasattr(self.client.tool_runtime, "list"):
                runtimes = await self.client.tool_runtime.list()
            else:
                logger.warning("Tool runtime listing method not found")
                return
            logger.info("Registered tool runtimes:")
            for runtime in runtimes:
                logger.info(
                    "  - %s: %s", runtime.tool_runtime_id, runtime.tool_runtime_type
                )
        except Exception as e:
            logger.warning("Failed to list tool runtimes: %s", e)

    async def test_mcp_tool(self) -> None:
        """Test the registered MCP tool."""
        if not self.client:
            raise RuntimeError("Not connected to Llama Stack")

        logger.info("Testing NextGenUI MCP tool...")

        try:
            # Test calling the MCP tool through Llama Stack
            test_input = {
                "user_prompt": "Show movie details",
                "input_data": [
                    {
                        "id": "movie1",
                        "data": '{"title": "Inception", "year": 2010, "director": "Christopher Nolan", "rating": 8.8}',
                    }
                ],
            }

            # Cast to the expected type for the API
            from typing import Any, Dict, cast

            test_input_typed = cast(Dict[str, Any], test_input)
            result = await self.client.tool_runtime.invoke_tool(
                tool_name="generate_ui", kwargs=test_input_typed
            )

            logger.info("MCP tool test successful!")
            logger.info("Result type: %s", type(result))
            logger.info("Result: %s", result)

        except Exception as e:
            logger.exception("MCP tool test failed: %s", e)
            logger.info("Make sure the NextGenUI MCP server is running and accessible")

    async def run(self, test_tool: bool = False) -> None:
        """Run the registration process."""
        try:
            await self.connect_to_llama_stack()
            await self.register_mcp_server()
            await self.list_tool_runtimes()

            if test_tool:
                await self.test_mcp_tool()

            logger.info("Registration completed successfully!")

        except Exception as e:
            logger.exception("Registration failed: %s", e)
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Register NextGenUI MCP server with existing Llama Stack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register with default Llama Stack URL
  python register_mcp_with_llamastack.py

  # Register with custom URL
  python register_mcp_with_llamastack.py --llama-url http://localhost:5001

  # Register and test the tool
  python register_mcp_with_llamastack.py --test

Prerequisites:
  - Llama Stack server must be running
  - NextGenUI MCP server must be available to start
        """,
    )

    parser.add_argument(
        "--llama-url",
        default=DEFAULT_LLAMA_STACK_URL,
        help=f"Llama Stack server URL (default: {DEFAULT_LLAMA_STACK_URL})",
    )
    parser.add_argument(
        "--mcp-command",
        nargs="+",
        default=DEFAULT_MCP_SERVER_COMMAND,
        help="Command to start MCP server (default: python libs/next_gen_ui_mcp/server_example.py)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test the MCP tool after registration",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Starting NextGenUI MCP server registration with Llama Stack")

    # Create manager
    manager = MCPRegistrationManager(
        llama_stack_url=args.llama_url,
        mcp_server_command=args.mcp_command,
    )

    # Run the registration
    try:
        asyncio.run(manager.run(test_tool=args.test))
    except KeyboardInterrupt:
        logger.info("Registration cancelled by user")
    except Exception as e:
        logger.exception("Registration failed: %s", e)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

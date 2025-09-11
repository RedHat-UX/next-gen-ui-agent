#!/usr/bin/env python3
"""
Script to start Llama Stack as a library and register NextGenUI MCP server.

This script demonstrates how to:
1. Start Llama Stack as an embedded library using AsyncLlamaStackAsLibraryClient
2. Register the NextGenUI MCP server with Llama Stack
3. Keep the server running for client connections

Usage:
    # Run with default configuration
    python start_llamastack_with_mcp.py

    # Run with custom llama-stack config file
    python start_llamastack_with_mcp.py --config /path/to/llamastack-config.yaml

    # Run with custom model
    python start_llamastack_with_mcp.py --model granite3.3:8b

    # Run with debug logging
    python start_llamastack_with_mcp.py --debug

The script will:
- Initialize Llama Stack as a library
- Register the NextGenUI MCP server (assumes server_example.py is running in stdio mode)
- Keep running until interrupted
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from llama_stack.distribution.library_client import AsyncLlamaStackAsLibraryClient
    from llama_stack_client.types.tool_runtime import ToolRuntimeConfig
except ImportError as e:
    print(f"Error: Llama Stack dependencies not found: {e}")
    print("Please install with: pip install llama-stack-client>=0.1.9,<=0.2.15")
    sys.exit(1)

from next_gen_ui_llama_stack.llama_stack_inference import LlamaStackAsyncAgentInference
from next_gen_ui_mcp.agent import NextGenUIMCPAgent

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG_FILE = "tests/ai_eval_components/llamastack-ollama.yaml"
DEFAULT_MODEL = "granite3.3:2b"
DEFAULT_MCP_SERVER_COMMAND = ["python", "libs/next_gen_ui_mcp/server_example.py"]


class LlamaStackMCPManager:
    """Manager for Llama Stack with MCP server integration."""

    def __init__(
        self,
        config_file: str,
        model: str,
        mcp_server_command: Optional[list[str]] = None,
    ):
        self.config_file = config_file
        self.model = model
        self.mcp_server_command = mcp_server_command or DEFAULT_MCP_SERVER_COMMAND
        self.llama_client: Optional[AsyncLlamaStackAsLibraryClient] = None
        self.mcp_agent: Optional[NextGenUIMCPAgent] = None

    async def initialize_llama_stack(self) -> None:
        """Initialize Llama Stack as a library."""
        logger.info(f"Initializing Llama Stack with config: {self.config_file}")
        logger.info(f"Using model: {self.model}")

        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Llama Stack config file not found: {self.config_file}")

        self.llama_client = AsyncLlamaStackAsLibraryClient(self.config_file)
        await self.llama_client.initialize()
        
        logger.info("Llama Stack initialized successfully")

    async def register_mcp_server(self) -> None:
        """Register the NextGenUI MCP server with Llama Stack."""
        if not self.llama_client:
            raise RuntimeError("Llama Stack client not initialized")

        logger.info("Registering NextGenUI MCP server...")
        logger.info(f"MCP server command: {' '.join(self.mcp_server_command)}")

        try:
            # Register the MCP server as a tool runtime
            tool_runtime_config = ToolRuntimeConfig(
                tool_runtime_type="mcp",
                config={
                    "command": self.mcp_server_command,
                    "env": {},  # Add any environment variables if needed
                }
            )

            # Register the tool runtime with Llama Stack
            await self.llama_client.tool_runtime.register_tool_runtime(
                tool_runtime_id="nextgen_ui_mcp",
                tool_runtime_config=tool_runtime_config
            )

            logger.info("NextGenUI MCP server registered successfully")

        except Exception as e:
            logger.error(f"Failed to register MCP server: {e}")
            raise

    async def create_mcp_agent(self) -> None:
        """Create NextGenUI MCP agent for testing purposes."""
        if not self.llama_client:
            raise RuntimeError("Llama Stack client not initialized")

        logger.info("Creating NextGenUI MCP agent for testing...")
        
        # Create inference provider using the embedded Llama Stack
        inference = LlamaStackAsyncAgentInference(self.llama_client, self.model)
        
        # Create MCP agent
        self.mcp_agent = NextGenUIMCPAgent(
            component_system="json",
            inference=inference,
            name="NextGenUI-MCP-Server-Embedded"
        )
        
        logger.info("NextGenUI MCP agent created successfully")

    async def run_server(self) -> None:
        """Keep the server running."""
        logger.info("Llama Stack with NextGenUI MCP server is now running...")
        logger.info("The MCP server is registered and available for tool calls")
        logger.info("Press Ctrl+C to stop the server")

        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

    async def start(self) -> None:
        """Start the complete setup."""
        try:
            await self.initialize_llama_stack()
            await self.register_mcp_server()
            await self.create_mcp_agent()
            await self.run_server()
        except Exception as e:
            logger.error(f"Failed to start Llama Stack with MCP: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Cleaning up resources...")
        if self.llama_client:
            # Add any cleanup logic if needed
            pass


async def test_mcp_integration(manager: LlamaStackMCPManager) -> None:
    """Test the MCP integration by calling the tool."""
    if not manager.llama_client:
        logger.error("Llama Stack client not available for testing")
        return

    logger.info("Testing MCP integration...")
    
    try:
        # Test calling the MCP tool through Llama Stack
        test_input = {
            "user_prompt": "Show movie details",
            "input_data": [
                {
                    "id": "movie1",
                    "data": '{"title": "Inception", "year": 2010, "director": "Christopher Nolan", "rating": 8.8}'
                }
            ]
        }

        result = await manager.llama_client.tool_runtime.invoke_tool(
            tool_name="generate_ui",
            kwargs=test_input
        )
        
        logger.info("MCP tool test successful!")
        logger.info(f"Result: {result}")
        
    except Exception as e:
        logger.warning(f"MCP tool test failed (this is expected if MCP server is not running): {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start Llama Stack as a library and register NextGenUI MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration
  python start_llamastack_with_mcp.py

  # Run with custom config and model
  python start_llamastack_with_mcp.py --config /path/to/config.yaml --model granite3.3:8b

  # Run with debug logging
  python start_llamastack_with_mcp.py --debug

Note: Make sure the NextGenUI MCP server (server_example.py) is available to be started.
        """,
    )

    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to Llama Stack configuration file (default: {DEFAULT_CONFIG_FILE})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--mcp-command",
        nargs="+",
        default=DEFAULT_MCP_SERVER_COMMAND,
        help="Command to start MCP server (default: python libs/next_gen_ui_mcp/server_example.py)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a test of the MCP integration after setup",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Starting Llama Stack with NextGenUI MCP server integration")

    # Create manager
    manager = LlamaStackMCPManager(
        config_file=args.config,
        model=args.model,
        mcp_server_command=args.mcp_command,
    )

    async def run_with_cleanup():
        try:
            await manager.start()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
        finally:
            await manager.cleanup()

    # Run the server
    try:
        asyncio.run(run_with_cleanup())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

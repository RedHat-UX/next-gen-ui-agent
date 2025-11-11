#!/usr/bin/env python3
"""
MCP SDK Client Example for NextGenUI MCP Server

This client demonstrates how to connect to a running NextGenUI MCP server
via SSE transport and use local Ollama for sampling inference.

Requirements:
- NextGenUI MCP server running on localhost:8000 (SSE transport)
- Ollama installed locally with a compatible model
- MCP SDK dependencies

Usage:
    # Start the MCP server first (in another terminal):
    python libs/next_gen_ui_mcp --transport sse --port 8000

    # Then run this client:
    python libs/next_gen_ui_mcp/mcp_client_example.py

    # Run with custom model:
    python libs/next_gen_ui_mcp/mcp_client_example.py --model llama3.2:3b

    # Run with debug logging:
    python libs/next_gen_ui_mcp/mcp_client_example.py --debug

The client will:
1. Connect to the NextGenUI MCP server via SSE
2. Set up Ollama-based sampling for LLM inference
3. Test the generate_ui_multiple_components tool with sample movie data
4. Display the generated UI components
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

# Check for required dependencies
try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
    from mcp.types import (
        INTERNAL_ERROR,
        CreateMessageRequest,
        CreateMessageResult,
        ErrorData,
        TextContent,
    )

    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    MCP_ERROR = (
        f"MCP SDK dependencies not found: {e}. Install with: pip install mcp>=1.12.0"
    )

    INTERNAL_ERROR = -32603

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OLLAMA_ERROR = "Ollama Python client not found. Install with: pip install ollama"

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_MCP_SERVER_URL = "http://localhost:8000/sse"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"

# Sample test data
SAMPLE_MOVIE_DATA = {
    "id": "movie_example",
    "data": json.dumps(
        {
            "title": "The Matrix",
            "year": 1999,
            "director": "The Wachowskis",
            "rating": 8.7,
            "genre": "Science Fiction",
            "runtime": 136,
            "plot": "A computer programmer discovers that reality as he knows it is a simulation.",
        }
    ),
}


class OllamaSamplingHandler:
    """Handles sampling requests using local Ollama."""

    def __init__(
        self, model: str = DEFAULT_OLLAMA_MODEL, host: str = DEFAULT_OLLAMA_HOST
    ):
        self.model = model
        self.host = host
        self.client: Optional[Any] = None

    async def initialize(self) -> None:
        """Initialize the Ollama client."""
        if not OLLAMA_AVAILABLE:
            raise RuntimeError(OLLAMA_ERROR)

        # Test Ollama connection
        try:
            self.client = ollama.AsyncClient(host=self.host)
            # Check if the model is available
            try:
                models = await self.client.list()
                available_models = []
                for model in models.get("models", []):
                    # Handle different possible model name fields
                    model_name = model.get("name") or model.get("model") or str(model)
                    available_models.append(model_name)

                if self.model not in available_models:
                    logger.warning(
                        "Model %s not found in Ollama. Available models: %s",
                        self.model,
                        available_models,
                    )
                    logger.info("Attempting to pull model %s...", self.model)
                    if self.client is not None:
                        await self.client.pull(self.model)
                    logger.info("Successfully pulled model %s", self.model)
                else:
                    logger.info("Model %s is available in Ollama", self.model)

            except Exception as model_error:
                logger.warning("Could not check available models: %s", model_error)
                logger.info("Assuming model %s is available", self.model)

        except Exception as e:
            raise RuntimeError(f"Failed to connect to Ollama at {self.host}: {e}")

    async def handle_sampling(
        self, request: CreateMessageRequest
    ) -> CreateMessageResult:
        """Handle a sampling request from the MCP server."""
        try:
            # Extract the messages and system prompt
            messages = []

            # Add system message if provided
            if hasattr(request, "system_prompt") and request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})

            # Add conversation messages
            if hasattr(request, "messages"):
                for msg in request.messages:
                    if isinstance(msg.content, TextContent):
                        messages.append({"role": msg.role, "content": msg.content.text})
                    elif isinstance(msg.content, str):
                        messages.append({"role": msg.role, "content": msg.content})
                    elif isinstance(msg.content, list):
                        # Handle multiple content items
                        content_text = ""
                        for item in msg.content:
                            if isinstance(item, TextContent):
                                content_text += item.text
                            elif hasattr(item, "text"):
                                content_text += item.text
                        messages.append({"role": msg.role, "content": content_text})

            logger.debug("Sending to Ollama: %s", messages)

            # Call Ollama
            if self.client is None:
                raise RuntimeError("Ollama client not initialized")

            response = await self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": getattr(request, "temperature", 0.0),
                    "top_p": getattr(request, "top_p", 1.0),
                    "max_tokens": getattr(request, "max_tokens", 4096),
                },
            )

            # Extract response text
            response_text = response["message"]["content"]
            logger.debug("Ollama response: %s", response_text)

            # Create MCP response
            return CreateMessageResult(
                content=TextContent(type="text", text=response_text),
                model=self.model,
                role="assistant",
                stopReason="stop",
            )

        except Exception as e:
            logger.exception("Sampling failed: %s", e)
            # Return error response
            return CreateMessageResult(
                content=TextContent(type="text", text=f"Error: {e}"),
                model=self.model,
                role="assistant",
                stopReason="error",
            )


class NextGenUIMCPClient:
    """MCP client for connecting to NextGenUI MCP server."""

    def __init__(self, server_url: str, ollama_model: str = DEFAULT_OLLAMA_MODEL):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self.sampling_handler = OllamaSamplingHandler(ollama_model)
        self._client_context: Optional[Any] = None

    async def connect(self) -> None:
        """Connect to the MCP server."""
        logger.info("Connecting to NextGenUI MCP server at %s", self.server_url)

        # Initialize Ollama
        await self.sampling_handler.initialize()
        logger.info("Ollama initialized with model: %s", self.sampling_handler.model)

        try:
            # Create SSE client session using async context manager
            if MCP_AVAILABLE:
                self._client_context = sse_client(self.server_url)
                read_stream, write_stream = await self._client_context.__aenter__()

                # Create client session with sampling callback
                from mcp.client.session import ClientSession

                # Create wrapper function that matches MCP SDK signature
                async def sampling_callback(context, params):
                    # Convert the params to CreateMessageRequest format expected by handle_sampling
                    return await self.sampling_handler.handle_sampling(params)

                self.session = ClientSession(
                    read_stream, write_stream, sampling_callback=sampling_callback
                )

                # Initialize the session
                await self.session.initialize()
            else:
                raise RuntimeError(MCP_ERROR)

            logger.info("Successfully connected to MCP server")

        except Exception as e:
            logger.exception("Failed to connect to MCP server: %s", e)
            raise

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        try:
            # Close the session first if it exists
            if self.session is not None:
                # Sessions don't typically need explicit closing, but clean up reference
                self.session = None

            # Then close the transport context
            if self._client_context is not None:
                await self._client_context.__aexit__(None, None, None)
                logger.info("Disconnected from MCP server")
        except Exception as e:
            logger.warning("Error during disconnect: %s", e)
        finally:
            self.session = None
            self._client_context = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            response = await self.session.list_tools()
            # Convert to list of dicts as expected by return type
            return [
                tool.__dict__ if hasattr(tool, "__dict__") else dict(tool)
                for tool in response.tools
            ]
        except Exception as e:
            logger.exception("Failed to list tools: %s", e)
            raise

    async def generate_ui(
        self, user_prompt: str, input_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Call the generate_ui tool."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            logger.info("Calling generate_ui tool...")
            logger.debug("User prompt: %s", user_prompt)
            logger.debug("Input data: %s", input_data)

            # Call the tool
            response = await self.session.call_tool(
                "generate_ui_multiple_components",
                {"user_prompt": user_prompt, "input_data": input_data},
            )

            logger.info("Successfully generated UI components")
            # Convert response to dict
            if hasattr(response, "__dict__"):
                return response.__dict__
            elif hasattr(response, "content"):
                return {"content": response.content}
            else:
                return dict(response) if response else {}

        except Exception as e:
            logger.exception("Failed to generate UI: %s", e)
            raise

    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            # Convert string to proper URL type if needed
            from typing import cast

            if MCP_AVAILABLE:
                try:
                    from mcp.types import AnyUrl  # type: ignore[attr-defined]

                    url = cast(AnyUrl, "system://info")
                except ImportError:
                    url = "system://info"  # type: ignore
            else:
                url = "system://info"  # type: ignore
            response = await self.session.read_resource(url)
            if response.contents:
                content = response.contents[0]
                if hasattr(content, "text"):
                    result = json.loads(content.text)
                    return result if isinstance(result, dict) else {}
                else:
                    result = json.loads(str(content))
                    return result if isinstance(result, dict) else {}
            return {}
        except Exception as e:
            logger.warning("Failed to get system info: %s", e)
            return {}


async def demo_ui_generation(server_url: str, ollama_model: str):
    """Demonstrate UI generation with the MCP client."""
    logger.info("🎬 Starting NextGenUI MCP Client Demo")

    # Initialize Ollama handler first
    sampling_handler = OllamaSamplingHandler(ollama_model)
    await sampling_handler.initialize()
    logger.info("Ollama initialized with model: %s", sampling_handler.model)

    # Create sampling callback function that matches MCP SDK signature
    # According to SDK docs: async def sampling_callback(context, params) -> CreateMessageResult | ErrorData
    async def sampling_callback(context, params):
        logger.info("🔄 Sampling callback called with params: %s", params)
        logger.debug("Context type: %s, Params type: %s", type(context), type(params))
        try:
            # The params are already in the correct format (CreateMessageRequestParams)
            # We need to handle the sampling request and return a CreateMessageResult

            # Extract messages from params
            if hasattr(params, "messages") and params.messages:
                messages = params.messages
                logger.debug("Processing %s messages", len(messages))

                # Extract user message and system prompt
                last_message = messages[-1]
                if hasattr(last_message, "content") and hasattr(
                    last_message.content, "text"
                ):
                    user_prompt = last_message.content.text
                elif hasattr(last_message, "content") and isinstance(
                    last_message.content, str
                ):
                    user_prompt = last_message.content
                else:
                    user_prompt = str(last_message.content)

                # Get system prompt from params
                system_prompt = getattr(params, "systemPrompt", "") or ""

                # Combine system and user prompts for Ollama
                if system_prompt:
                    full_prompt = (
                        f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
                    )
                else:
                    full_prompt = user_prompt

                logger.info(
                    "🔍 Sending to Ollama - System: %s chars, User: %s chars",
                    len(system_prompt),
                    len(user_prompt),
                )
                logger.debug("Full prompt preview: %s...", repr(full_prompt[:200]))

                # Use Ollama to generate response
                response = await sampling_handler.client.generate(
                    model=sampling_handler.model, prompt=full_prompt, stream=False
                )

                response_text = response.get("response", "")
                logger.info("✅ Ollama response received: %s chars", len(response_text))
                # Log the actual response to help debug JSON parsing issues
                logger.info(
                    "🔍 First 300 chars of Ollama response: %s",
                    repr(response_text[:300]),
                )
                if len(response_text) > 300:
                    logger.info(
                        "🔍 Last 100 chars of Ollama response: %s",
                        repr(response_text[-100:]),
                    )

                # Return CreateMessageResult with TextContent
                # Include model field as required by MCP specification
                model_name = (
                    getattr(params, "modelPreferences", {}) or sampling_handler.model
                )
                if hasattr(model_name, "get"):
                    model_name = model_name.get("name", sampling_handler.model)
                elif model_name is None:
                    model_name = sampling_handler.model

                return CreateMessageResult(
                    model=model_name,
                    role="assistant",
                    content=TextContent(type="text", text=response_text),
                )
            else:
                logger.warning("No messages found in sampling params")
                return ErrorData(
                    code=INTERNAL_ERROR, message="No messages provided for sampling"
                )
        except Exception as e:
            logger.exception("❌ Sampling failed: %s", e)
            import traceback

            logger.debug("Sampling error details: %s", traceback.format_exc())
            # Return error data as expected by MCP
            return ErrorData(code=INTERNAL_ERROR, message=f"Sampling failed: {e}")

    # Use SSE client with proper async context manager following official MCP SDK patterns
    logger.info("🔄 Connecting to MCP server via SSE at %s", server_url)
    async with sse_client(server_url) as (read_stream, write_stream):
        logger.info("✅ Connected to NextGenUI MCP server at %s", server_url)
        logger.debug(
            "🔄 Got streams - read: %s, write: %s",
            type(read_stream),
            type(write_stream),
        )

        # Use ClientSession as async context manager with sampling callback (following official SDK pattern)
        logger.info("🔄 Creating ClientSession with sampling callback...")
        async with ClientSession(
            read_stream, write_stream, sampling_callback=sampling_callback
        ) as session:
            logger.info("✅ ClientSession created successfully")

            # Initialize the session (this should happen automatically with the context manager)
            logger.info("🔄 Starting MCP session initialization...")
            try:
                # According to SDK docs, initialize() is called automatically by the context manager
                # but we can call it explicitly if needed
                init_result = await asyncio.wait_for(session.initialize(), timeout=30.0)
                logger.info("✅ MCP session initialized successfully: %s", init_result)
            except asyncio.TimeoutError:
                logger.exception(
                    "❌ MCP session initialization timed out after 30 seconds"
                )
                raise
            except Exception as e:
                logger.exception("❌ MCP session initialization failed: %s", e)
                import traceback

                logger.debug("Initialization error details: %s", traceback.format_exc())
                raise

            # Get system info
            logger.info("📋 Getting system information...")
            try:
                logger.debug("🔄 Calling session.read_resource('system://info')...")
                # Handle AnyUrl type requirement
                if MCP_AVAILABLE:
                    try:
                        from mcp.types import AnyUrl  # type: ignore[attr-defined]

                        system_url = AnyUrl("system://info")
                    except ImportError:
                        system_url = "system://info"  # type: ignore
                else:
                    system_url = "system://info"  # type: ignore
                system_info_response = await session.read_resource(system_url)
                logger.debug(
                    "✅ Got system info response: %s", type(system_info_response)
                )

                if system_info_response.contents:
                    content = system_info_response.contents[0]
                    if hasattr(content, "text"):
                        system_info = json.loads(content.text)
                    else:
                        system_info = json.loads(str(content))
                    logger.info(
                        "Connected to: %s", system_info.get("agent_name", "Unknown")
                    )
                    logger.info(
                        "Component system: %s",
                        system_info.get("component_system", "Unknown"),
                    )
                else:
                    logger.warning("System info response has no contents")
            except Exception as e:
                logger.warning("Could not get system info: %s", e)
                import traceback

                logger.debug("System info error details: %s", traceback.format_exc())

            # List available tools
            logger.info("🔧 Listing available tools...")
            try:
                logger.debug("🔄 Calling session.list_tools()...")
                tools_response = await session.list_tools()
                logger.debug("✅ Got tools response: %s", type(tools_response))
                logger.info(
                    "Available tools: %s", [tool.name for tool in tools_response.tools]
                )
            except Exception as e:
                logger.warning("Could not list tools: %s", e)
                import traceback

                logger.debug("List tools error details: %s", traceback.format_exc())

            # Test UI generation
            logger.info("🎨 Generating UI for movie data...")
            user_prompt = "Create a movie information card showing the key details"
            input_data = [SAMPLE_MOVIE_DATA]

            logger.debug(
                "🔄 Calling generate_ui_multiple_components tool with prompt: '%s'",
                user_prompt,
            )
            logger.debug("🔄 Input data: %s", input_data)

            try:
                result = await session.call_tool(
                    name="generate_ui_multiple_components",
                    arguments={"user_prompt": user_prompt, "input_data": input_data},
                )
                logger.debug("✅ Got tool result: %s", type(result))
            except Exception as e:
                logger.exception("❌ Tool call failed: %s", e)
                import traceback

                logger.debug("Tool call error details: %s", traceback.format_exc())
                raise

            # Display results
            logger.info("✅ UI Generation Complete!")
            logger.info("=" * 50)
            logger.info("Generated UI Components:")
            logger.info("=" * 50)

            if hasattr(result, "content") and result.content:
                for item in result.content:
                    if hasattr(item, "text"):
                        try:
                            ui_data = json.loads(item.text)
                            print(json.dumps(ui_data, indent=2))
                        except json.JSONDecodeError:
                            print(item.text)
                    else:
                        print(str(item))
            else:
                print(json.dumps(result, indent=2, default=str))

        logger.info("=" * 50)
        logger.info("🎉 Demo completed successfully!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NextGenUI MCP Client Example with Ollama Sampling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect to default server and run demo
  python mcp_client_example.py

  # Use different model
  python mcp_client_example.py --model llama3.2:1b

  # Use different server URL
  python mcp_client_example.py --server-url http://localhost:9000/sse

  # Enable debug logging
  python mcp_client_example.py --debug

Prerequisites:
  1. Start NextGenUI MCP server:
     python libs/next_gen_ui_mcp/server_example.py --transport sse --port 8000

  2. Ensure Ollama is running with a compatible model:
     ollama serve
     ollama pull llama3.2:3b
        """,
    )

    parser.add_argument(
        "--server-url",
        default=DEFAULT_MCP_SERVER_URL,
        help=f"MCP server URL (default: {DEFAULT_MCP_SERVER_URL})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_OLLAMA_MODEL,
        help=f"Ollama model to use for sampling (default: {DEFAULT_OLLAMA_MODEL})",
    )
    parser.add_argument(
        "--ollama-host",
        default=DEFAULT_OLLAMA_HOST,
        help=f"Ollama host URL (default: {DEFAULT_OLLAMA_HOST})",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Check dependencies
    if not MCP_AVAILABLE:
        print(f"❌ {MCP_ERROR}")
        sys.exit(1)

    if not OLLAMA_AVAILABLE:
        print(f"❌ {OLLAMA_ERROR}")
        sys.exit(1)

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run demo
    try:
        asyncio.run(demo_ui_generation(args.server_url, args.model))
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.exception("Demo failed: %s", e)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

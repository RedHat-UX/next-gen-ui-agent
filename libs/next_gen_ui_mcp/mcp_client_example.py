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
    python libs/next_gen_ui_mcp/server_example.py --transport sse --port 8000

    # Then run this client:
    python libs/next_gen_ui_mcp/mcp_client_example.py

    # Run with custom model:
    python libs/next_gen_ui_mcp/mcp_client_example.py --model llama3.2:3b

    # Run with debug logging:
    python libs/next_gen_ui_mcp/mcp_client_example.py --debug

The client will:
1. Connect to the NextGenUI MCP server via SSE
2. Set up Ollama-based sampling for LLM inference
3. Test the generate_ui tool with sample movie data
4. Display the generated UI components
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add libs to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check for required dependencies
try:
    import httpx
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.sse import sse_client
    from mcp.client.stdio import stdio_client
    from mcp.types import (
        CallToolRequest,
        CreateMessageRequest,
        CreateMessageResponse,
        SamplingMessage,
        TextContent,
    )
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    MCP_ERROR = f"MCP SDK dependencies not found: {e}. Install with: pip install mcp>=1.12.0"
    
    # Create dummy classes for when MCP is not available
    class CreateMessageRequest:
        pass
    class CreateMessageResponse:
        pass
    class TextContent:
        pass
    class CallToolRequest:
        pass

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
    "data": json.dumps({
        "title": "The Matrix",
        "year": 1999,
        "director": "The Wachowskis", 
        "rating": 8.7,
        "genre": "Science Fiction",
        "runtime": 136,
        "plot": "A computer programmer discovers that reality as he knows it is a simulation."
    })
}


class OllamaSamplingHandler:
    """Handles sampling requests using local Ollama."""
    
    def __init__(self, model: str = DEFAULT_OLLAMA_MODEL, host: str = DEFAULT_OLLAMA_HOST):
        self.model = model
        self.host = host
        self.client = None
        
    async def initialize(self) -> None:
        """Initialize the Ollama client."""
        if not OLLAMA_AVAILABLE:
            raise RuntimeError(OLLAMA_ERROR)
            
        # Test Ollama connection
        try:
            self.client = ollama.AsyncClient(host=self.host)
            # Check if the model is available
            models = await self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model not in available_models:
                logger.warning(f"Model {self.model} not found in Ollama. Available models: {available_models}")
                logger.info(f"Attempting to pull model {self.model}...")
                await self.client.pull(self.model)
                logger.info(f"Successfully pulled model {self.model}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Ollama at {self.host}: {e}")
    
    async def handle_sampling(self, request: CreateMessageRequest) -> CreateMessageResponse:
        """Handle a sampling request from the MCP server."""
        try:
            # Extract the messages and system prompt
            messages = []
            
            # Add system message if provided
            if request.system_prompt:
                messages.append({
                    "role": "system",
                    "content": request.system_prompt
                })
            
            # Add conversation messages
            for msg in request.messages:
                if isinstance(msg.content, TextContent):
                    messages.append({
                        "role": msg.role,
                        "content": msg.content.text
                    })
                elif isinstance(msg.content, str):
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                elif isinstance(msg.content, list):
                    # Handle multiple content items
                    content_text = ""
                    for item in msg.content:
                        if isinstance(item, TextContent):
                            content_text += item.text
                        elif hasattr(item, 'text'):
                            content_text += item.text
                    messages.append({
                        "role": msg.role,
                        "content": content_text
                    })
            
            logger.debug(f"Sending to Ollama: {messages}")
            
            # Call Ollama
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": getattr(request, 'temperature', 0.0),
                    "top_p": getattr(request, 'top_p', 1.0),
                    "max_tokens": getattr(request, 'max_tokens', 4096),
                }
            )
            
            # Extract response text
            response_text = response['message']['content']
            logger.debug(f"Ollama response: {response_text}")
            
            # Create MCP response
            return CreateMessageResponse(
                content=TextContent(type="text", text=response_text),
                model=self.model,
                role="assistant",
                stop_reason="stop"
            )
            
        except Exception as e:
            logger.error(f"Sampling failed: {e}")
            # Return error response
            return CreateMessageResponse(
                content=TextContent(type="text", text=f"Error: {e}"),
                model=self.model,
                role="assistant", 
                stop_reason="error"
            )


class NextGenUIMCPClient:
    """MCP client for connecting to NextGenUI MCP server."""
    
    def __init__(self, server_url: str, ollama_model: str = DEFAULT_OLLAMA_MODEL):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self.sampling_handler = OllamaSamplingHandler(ollama_model)
        
    async def connect(self) -> None:
        """Connect to the MCP server."""
        logger.info(f"Connecting to NextGenUI MCP server at {self.server_url}")
        
        # Initialize Ollama
        await self.sampling_handler.initialize()
        logger.info(f"Ollama initialized with model: {self.sampling_handler.model}")
        
        try:
            # Create SSE client session
            self.session = await sse_client(self.server_url)
            
            # Set up sampling handler
            self.session.sampling_handler = self.sampling_handler.handle_sampling
            
            # Initialize the session
            await self.session.initialize()
            
            logger.info("Successfully connected to MCP server")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            logger.info("Disconnected from MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.list_tools()
            return response.tools
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    async def generate_ui(self, user_prompt: str, input_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call the generate_ui tool."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            logger.info("Calling generate_ui tool...")
            logger.debug(f"User prompt: {user_prompt}")
            logger.debug(f"Input data: {input_data}")
            
            # Call the tool
            response = await self.session.call_tool(
                CallToolRequest(
                    name="generate_ui",
                    arguments={
                        "user_prompt": user_prompt,
                        "input_data": input_data
                    }
                )
            )
            
            logger.info("Successfully generated UI components")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate UI: {e}")
            raise
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.session.read_resource("system://info")
            if response.contents:
                content = response.contents[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
                else:
                    return json.loads(str(content))
            return {}
        except Exception as e:
            logger.warning(f"Failed to get system info: {e}")
            return {}


async def demo_ui_generation(client: NextGenUIMCPClient):
    """Demonstrate UI generation with the MCP client."""
    logger.info("🎬 Starting NextGenUI MCP Client Demo")
    
    try:
        # Connect to server
        await client.connect()
        
        # Get system info
        logger.info("📋 Getting system information...")
        system_info = await client.get_system_info()
        if system_info:
            logger.info(f"Connected to: {system_info.get('agent_name', 'Unknown')}")
            logger.info(f"Component system: {system_info.get('component_system', 'Unknown')}")
        
        # List available tools
        logger.info("🔧 Listing available tools...")
        tools = await client.list_tools()
        logger.info(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # Test UI generation
        logger.info("🎨 Generating UI for movie data...")
        user_prompt = "Create a movie information card showing the key details"
        input_data = [SAMPLE_MOVIE_DATA]
        
        result = await client.generate_ui(user_prompt, input_data)
        
        # Display results
        logger.info("✅ UI Generation Complete!")
        logger.info("=" * 50)
        logger.info("Generated UI Components:")
        logger.info("=" * 50)
        
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if hasattr(item, 'text'):
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
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise
    finally:
        await client.disconnect()


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
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create client
    client = NextGenUIMCPClient(
        server_url=args.server_url,
        ollama_model=args.model
    )

    # Run demo
    try:
        asyncio.run(demo_ui_generation(client))
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

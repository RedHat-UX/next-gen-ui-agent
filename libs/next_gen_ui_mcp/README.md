# Next Gen UI MCP Server

This package wraps our NextGenUI agent in a Model Context Protocol (MCP) tool using the standard MCP SDK. Since MCP adoption is so strong these days and there is an apetite to use this protocol also for handling agentic AI, we wanted to also deliver this way of consuming our agent. Saying that the current vision for MCP tools is to provide them to LLM to choose and execute with certain parameters. This approach doesn't make sense for NextGenUI agent as you want to call it at specific moment after gathering data for response and also you don't want LLM to try to pass the prompt and JSON content as it makes no sense. It's more natural and reliable to invoke this MCP tool directly with the parameters as part of your main application logic.

## Installation

```sh
pip install -U next_gen_ui_mcp
```

Additionally you'll also need one of inference providers to run the MCP agent. You can find one in next_gen_ui_beeai or next_gen_ui_llama_stack packages.

## Example

### Testing with Real MCP Clients

The package includes comprehensive tests that demonstrate both direct server testing and real client-server communication:

- `agent_test.py` - Contains multiple test scenarios including realistic client-server tests
- `server_example.py` - Standalone server for testing with external MCP clients

#### Running the standalone server:

```bash
# Run with stdio (for command-line MCP clients)
python libs/next_gen_ui_mcp/server_example.py

# Run with HTTP SSE (for web-based clients)
python libs/next_gen_ui_mcp/server_example.py --transport sse --port 8000

# Run with streamable HTTP
python libs/next_gen_ui_mcp/server_example.py --transport streamable-http --port 8000
```

#### Testing with MCP Client:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_client():
    server_params = StdioServerParameters(
        command="python",
        args=["libs/next_gen_ui_mcp/server_example.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools])
            
            # Call the generate_ui tool
            result = await session.call_tool("generate_ui", {
                "user_prompt": "Show movie details",
                "input_data": [{"id": "movie1", "data": '{"title": "Inception", "year": 2010}'}]
            })
            print("Result:", result)

asyncio.run(test_client())
```

### Using NextGenUI MCP Agent through Llama Stack

[Llama-stack documentation for tools](https://llama-stack.readthedocs.io/en/latest/building_applications/tools.html) nicely shows how to register a MCP server but also shows the below code on how to invoke a tool directly

```python
result = client.tool_runtime.invoke_tool(tool_name="generate_ui", kwargs=input_data)
)
```

## Available MCP Tools

### `generate_ui`
The main tool that wraps the entire Next Gen UI Agent functionality. This single tool handles:
- Component selection based on user prompt and data
- Data transformation to match selected components  
- Design system rendering to produce final UI

**Parameters:**
- `user_prompt` (str): User's prompt which we want to enrich with UI components
- `input_data` (List[Dict]): List of input data to render within the UI components

**Returns:**
- List of rendered UI components ready for display

## Available MCP Resources

### `system://info`
Returns system information about the Next Gen UI Agent including:
- Agent name
- Component system being used
- Available capabilities
- Description

## Running Different Transports

### Stdio (Default)
```py
agent.run()  # Uses stdio transport by default
```

### Server-Sent Events (SSE)
```py
agent.run(transport="sse", host="127.0.0.1", port=8000)
```

### Streamable HTTP
```py
agent.run(transport="streamable-http", host="127.0.0.1", port=8000)
```

## Llama Stack Integration

### Starting Llama Stack as Library with MCP Server

Use `start_llamastack_with_mcp.py` to start Llama Stack as an embedded library and register the NextGenUI MCP server:

```bash
# Run with default configuration
python libs/next_gen_ui_mcp/start_llamastack_with_mcp.py

# Run with custom config and model
python libs/next_gen_ui_mcp/start_llamastack_with_mcp.py --config /path/to/llamastack-config.yaml --model granite3.3:8b

# Run with debug logging
python libs/next_gen_ui_mcp/start_llamastack_with_mcp.py --debug
```

This script will:
1. Initialize Llama Stack as a library using `AsyncLlamaStackAsLibraryClient`
2. Register the NextGenUI MCP server as a tool runtime
3. Keep the server running for client connections

### Registering MCP Server with Existing Llama Stack

If you already have Llama Stack running, use `register_mcp_with_llamastack.py` to register the NextGenUI MCP server:

```bash
# Register with default Llama Stack URL (http://localhost:5001)
python libs/next_gen_ui_mcp/register_mcp_with_llamastack.py

# Register with custom URL
python libs/next_gen_ui_mcp/register_mcp_with_llamastack.py --llama-url http://localhost:5001

# Register and test the tool
python libs/next_gen_ui_mcp/register_mcp_with_llamastack.py --test
```

### Using the Registered MCP Tool

Once registered, you can invoke the NextGenUI tool through Llama Stack:

```python
from llama_stack_client import AsyncLlamaStackClient

client = AsyncLlamaStackClient(base_url="http://localhost:5001")

# Call the NextGenUI MCP tool
result = await client.tool_runtime.invoke_tool(
    tool_name="generate_ui",
    kwargs={
        "user_prompt": "Show movie details",
        "input_data": [
            {
                "id": "movie1", 
                "data": '{"title": "Inception", "year": 2010, "director": "Christopher Nolan"}'
            }
        ]
    }
)
```

## Component Systems

The agent supports various component systems such as:
- `rhds` - Red Hat Design System, available through `next_gen_ui_rhds_renderer` package
- `patternfly` - PatternFly Design System, available through `next_gen_ui_patternfly_renderer` package
- `json` - JSON renderer for testing, available by default
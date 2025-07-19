# Next Gen UI MCP Server

This package wraps our NextGenUI agent in a Model Context Protocol (MCP) tool. Since MCP adoption is so strong these days and there is apetite to use this protocol also for handling agentic AI, we wanted to also deliver this way of consuming our agent.

## Installation

```sh
pip install -U next_gen_ui_mcp
```

Additionally you'll also need one of inference providers to run the MCP agent. You can find one in next_gen_ui_beeai or next_gen_ui_llama_stack packages.

## Example

### A standalone example with use of FastMCP client

Please refer to `agent_test.py` file

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

### HTTP
```py
agent.run(transport="http", host="127.0.0.1", port=8000)
```

### Server-Sent Events (SSE)
```py
agent.run(transport="sse", host="127.0.0.1", port=8000)
```

## Component Systems

The agent supports various component systems such as:
- `rhds` - Red Hat Design System, available through `next_gen_ui_rhds_renderer` package
- `patternfly` - PatternFly Design System, available through `next_gen_ui_patternfly_renderer` package
- `json` - JSON renderer for testing, available by default
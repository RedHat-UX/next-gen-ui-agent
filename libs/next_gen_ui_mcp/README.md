# Next Gen UI MCP Server Library

This package wraps our NextGenUI agent in a Model Context Protocol (MCP) tool using the standard MCP SDK. Since MCP adoption is so strong these days and there is an apetite to use this protocol also for handling agentic AI, we wanted to also deliver this way of consuming our agent. The most common way of utilising MCP tools is to provide them to LLM to choose and execute with certain parameters. This approach doesn't make sense for NextGenUI agent as you want to call it at specific moment after gathering data for response and also you don't want LLM to try to pass the prompt and JSON content as it may lead to unnecessary errors in the content. It's more natural and reliable to invoke this MCP tool directly with the parameters as part of your main application logic.

## Installation

```sh
pip install -U next_gen_ui_mcp
```

Depending on your use case you may need additional packages for inference provider or design component renderers. More about this in the next sections.

## Usage

### Running the standalone server:

```bash
  # Run with MCP sampling (default - leverages client's LLM)
  python -m next_gen_ui_mcp

  # Run with LlamaStack inference
  python -m next_gen_ui_mcp --provider llamastack --model llama3.2-3b --llama-url http://localhost:5001

  # Run with LangChain OpenAI inference
  python -m next_gen_ui_mcp --provider langchain --model gpt-3.5-turbo

  # Run with LangChain via Ollama (local)
  python -m next_gen_ui_mcp --provider langchain --model llama3.2 --base-url http://localhost:11434/v1 --api-key ollama

  # Run with MCP sampling and custom max tokens
  python -m next_gen_ui_mcp --sampling-max-tokens 4096

  # Run with SSE transport (for web clients)
  python -m next_gen_ui_mcp --transport sse --host 127.0.0.1 --port 8000

  # Run with streamable-http transport
  python -m next_gen_ui_mcp --transport streamable-http --host 127.0.0.1 --port 8000

  # Run with patternfly component system
  python -m next_gen_ui_mcp --component-system rhds

  # Run with rhds component system via SSE transport
  python -m next_gen_ui_mcp --transport sse --component-system rhds --port 8000
```

As the above examples show you can choose to configure `llamastack` or `langchain` provided. You have to add the necessary dependencies to your python environment to do so, otherwise the application will complain about them missing

Similarly pluggable component systems such as `rhds` also require certain imports, `next_gen_ui_rhds_renderer` in this particular case.

If you are running this from inside of our [NextGenUI Agent GitHub repo](https://github.com/RedHat-UX/next-gen-ui-agent) then our `pants` repository manager can help you satisfy all dependencies. In such case you can run the commands in the following way:

```bash
  # Run with MCP sampling (default - leverages client's LLM)
  pants run libs/next_gen_ui_mcp/server_example.py:extended

  # Run with streamable-http transport and Red Hat Design System component system for rendering
  pants run libs/next_gen_ui_mcp/server_example.py:extended --run-args="--transport streamable-http --component-system rhds"
```

### Testing with MCP Client:

As part of the GitHub repository we also provide [an example client](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_mcp/mcp_client_example.py). This example client implementation uses MCP SDK client libraries and ollama for MCP sampling inference provision.

You can run it via this command:

```bash
pants --concurrent run libs/next_gen_ui_mcp/mcp_client_example.py
```
The `--concurrent` parameter is there only to allow calling it while you use `pants run` for starting the server. By default `pants` restrict parallel invocations.

### Using NextGenUI MCP Agent through Llama Stack

[Llama-stack documentation for tools](https://llama-stack.readthedocs.io/en/latest/building_applications/tools.html) nicely shows how to register a MCP server but also shows the below code on how to invoke a tool directly

```python
result = client.tool_runtime.invoke_tool(tool_name="generate_ui", kwargs=input_data)
)
```

## Available MCP Tools

### `generate_ui`
The main tool that wraps the entire Next Gen UI Agent functionality.

This single tool handles:

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

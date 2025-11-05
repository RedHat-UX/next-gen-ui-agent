# Next Gen UI MCP Server Library

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This package wraps Next Gen UI Agent in a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) tools using the [official Python MCP SDK](https://modelcontextprotocol.io/docs/sdk).

Since MCP adoption is so strong these days and there is an apetite to use this protocol also for handling agentic AI, we also deliver UI Agent this way. The most common way of utilising MCP tools is to provide them to LLM to choose and execute with certain parameters. This approach doesn't make too much sense for Next Gen UI Agent, as you want to call it at the specific moment, after gathering structured backend data for response. 
Also you don't want LLM to try to pass the prompt and JSON content as it may lead to unnecessary errors in the content. 
It's more natural and reliable to invoke this MCP tool directly with the parameters as part of your main application logic, also saving LLM tokens/price.

## Provides

* `__main__.py` to run the MCP server as the standalone server
* `NextGenUIMCPServer` to embed the UI Agent MCP server into your python code

## Installation

```sh
pip install -U next_gen_ui_mcp
```

Depending on your use case you may need additional packages for inference provider or design component renderers. More about this in the next sections.

## Usage

### Running the standalone server examples

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

### Server arguments

To get help how to run the server and pass the arguments run it with `-h` parameter:

```sh
python -m next_gen_ui_mcp -h

Next Gen UI MCP Server with Sampling or External LLM Providers

options:
  -h, --help            show this help message and exit
  --config-path CONFIG_PATH [CONFIG_PATH ...]
                        Path to configuration YAML file. You can specify multiple config files by repeating same parameter or passing comma separated value.
  --transport {stdio,sse,streamable-http}
                        Transport protocol to use
  --host HOST           Host to bind to
  --tools TOOLS [TOOLS ...]
                        Control which tools should be enabled. You can specify multiple values by repeating same parameter or passing comma separated value.
  --port PORT           Port to bind to
  --structured_output_enabled {true,false}
                        Control if structured output is used. If not enabled the ouput is serialized as JSON in content property only.
  --component-system {json,patternfly,rhds}
                        Component system to use for rendering (default: json)
  --debug               Enable debug logging
  --provider {mcp,llamastack,langchain}
                        Inference provider to use (default: mcp - uses MCP sampling)
  --model MODEL         Model name to use (required for llamastack and langchain)
  --llama-url LLAMA_URL
                        LlamaStack server URL (default: http://localhost:5001)
  --base-url BASE_URL   Base URL for OpenAI-compatible API (e.g., http://localhost:11434/v1 for Ollama)
  --api-key API_KEY     API key for the LLM provider (uses OPENAI_API_KEY env var if not provided)
  --temperature TEMPERATURE
                        Temperature for LangChain model (default: 0.0 for deterministic responses)
  --sampling-max-tokens SAMPLING_MAX_TOKENS
                        Maximum tokens for MCP sampling inference (default: 2048)
```

### Running Server locally from Git Repo

If you are running this from inside of our [NextGenUI Agent GitHub repo](https://github.com/RedHat-UX/next-gen-ui-agent) then our `pants` repository manager can help you satisfy all dependencies. In such case you can run the commands in the following way:

```bash
  # Run with MCP sampling (default - leverages client's LLM)
  pants run libs/next_gen_ui_mcp/server_example.py:extended

  # Run with streamable-http transport and Red Hat Design System component system for rendering
  pants run libs/next_gen_ui_mcp/server_example.py:extended --run-args="--transport streamable-http --component-system rhds"

  # Run directly
  PYTHONPATH=./libs python libs/next_gen_ui_mcp -h
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
result = client.tool_runtime.invoke_tool(
    tool_name="generate_ui_component",
    kwargs=input_data,
)
```

## Available MCP Tools

### `generate_ui_multiple_components`
The main tool that wraps the entire Next Gen UI Agent functionality.

This single tool handles:

- Component selection based on user prompt and data
- Data transformation to match selected components  
- Design system rendering to produce final UI

**Parameters:**

- `user_prompt` (str, required): User's prompt which we want to enrich with UI components
- `structured_data` (List[Dict], required): List of structured input data. Each object has to have `id`, `data` and `type` field.

You can find the input schema in [spec/mcp/generate_ui_input.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/mcp/generate_ui_input.schema.json).

**Returns:**

Object containing:

- UI blocks with rendering and configuration
- summary

When error occurs during the execution valid ui blocks are rendered. The failing UI Block is mentioned in the summary and don't appear in `blocks` field.


By default the result is provided as [structured content](https://modelcontextprotocol.io/specification/2025-06-18/server/tools#structured-content) where structured content contains JSON object and the text content just "human readable summary".
It's beneficial to send to Agent only text summary for LLM processing and use structured content for UI rendering on client side.

If it's disabled via --structured_output_enabled=false then there is no structured content in the result and the text content contains
the same content but as serialized JSON string.

For compatibility the JSON object contains the summary as well.

Example:

```json
{
  "blocks": [
    {
      "id": "e5e2db10-de22-4165-889c-02de2f24c901",
      "rendering": {
        "id": "e5e2db10-de22-4165-889c-02de2f24c901",
        "component_system": "json",
        "mime_type": "application/json",
        "content": "{\"component\":\"one-card\",\"image\":\"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg\",\"id\":\"e5e2db10-de22-4165-889c-02de2f24c901\",\"title\":\"Toy Story Movie Details\",\"fields\":[{\"name\":\"Title\",\"data_path\":\"$..movie_detail.title\",\"data\":[\"Toy Story\"]},{\"name\":\"Release Year\",\"data_path\":\"$..movie_detail.year\",\"data\":[1995]},{\"name\":\"IMDB Rating\",\"data_path\":\"$..movie_detail.imdbRating\",\"data\":[8.3]},{\"name\":\"Runtime (min)\",\"data_path\":\"$..movie_detail.runtime\",\"data\":[81]},{\"name\":\"Plot\",\"data_path\":\"$..movie_detail.plot\",\"data\":[\"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.\"]}]}"
      },
      "configuration": {
        "data_type": "movie_detail",
        "input_data_transformer_name": "json",
        "json_wrapping_field_name": "movie_detail",
        "component_metadata": {
          "id": "e5e2db10-de22-4165-889c-02de2f24c901",
          "title": "Toy Story Movie Details",
          "component": "one-card",
          "fields": [
            {
              "name": "Title",
              "data_path": "$..movie_detail.title"
            },
            {
              "name": "Release Year",
              "data_path": "$..movie_detail.year"
            },
            {
              "name": "IMDB Rating",
              "data_path": "$..movie_detail.imdbRating"
            },
            {
              "name": "Runtime (min)",
              "data_path": "$..movie_detail.runtime"
            },
            {
              "name": "Plot",
              "data_path": "$..movie_detail.plot"
            },
            {
              "name": "Poster",
              "data_path": "$..movie_detail.posterUrl"
            }
          ]
        }
      }
    }
  ],
  "summary": "Components are rendered in UI.\nCount: 1\n1. Title: 'Toy Story Movie Details', type: one-card"
}
```

You can find schema for the reponse in [spec/mcp/generate_ui_output.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/mcp/generate_ui_output.schema.json).

### `generate_ui_component`
The tool that wraps the entire Next Gen UI Agent functionality and with decomposed one input object into individual arguments.

Useful for agents which are able to pass one tool cool result to another.

When error occures, whole tool execution fails.

**Parameters:**

- `user_prompt` (str, required): User's prompt which we want to enrich with UI components
- `data` (str, required): Raw input data to render within the UI components
- `data_type` (str, required): Data type
- `data_id` (str, optional): ID of Data. If not present, ID is generated.

**Returns:**

Same result as `generate_ui_multiple_components` tool.

## Available MCP Resources

### `system://info`
Returns system information about the Next Gen UI Agent including:

- Agent name
- Component system being used
- Available capabilities
- Description

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_mcp)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)

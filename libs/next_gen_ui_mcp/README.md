# Next Gen UI MCP Server

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

This package wraps Next Gen UI Agent in a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) tools using the [official Python MCP SDK](https://modelcontextprotocol.io/docs/sdk).

Since MCP adoption is so strong these days and there is an apetite to use this protocol also for handling agentic AI, we also deliver UI Agent this way. 

The most common way of utilising MCP tools is to provide them to LLM to choose and execute with certain parameters. 
This approach of using Next Gen UI Agent makes sense if you want your AI Orchestrator give a chance to decide about the UI component generation.
For example to select which backend data loaded during the processing needs to be visualized in UI.
You have to prompt LLM in a way to pass the correct user prompt and structured backend data content into the UI MCP unaltered, to prevent unexpected UI errors. 

Alternative approach is to invoke this MCP tool directly (or even using another AI framework binding) with the parameters 
as part of your main application logic at the specific moment of the flow, after gathering structured backend data for response.
This approach is a bit more reliable, helps to reduce main LLM processing price (tokens) and saves processing time, but is less flexible.

## Provides

* `__main__.py` to run the MCP server as the standalone server
* `NextGenUIMCPServer` to embed the UI Agent MCP server into your python code

## Installation

**Note:** alternatively, you can use [container image](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-container/) to easily install and run the server.

```sh
pip install -U next_gen_ui_mcp
```

Depending on your use case you may need additional packages for inference provider or design component renderers. More about this in the next sections.

## Usage

### Running the standalone server

To get help how to run the server and pass the arguments run it with `-h` parameter:

```sh
python -m next_gen_ui_mcp -h

```

Few examples:

```bash
  # Run with MCP sampling (default - leverages client's LLM)
  python -m next_gen_ui_mcp

  # Run with OpenAI inference
  python -m next_gen_ui_mcp --provider openai --model gpt-3.5-turbo

  # Run with OpenAI compatible API of Ollama (local)
  python -m next_gen_ui_mcp --provider openai --model llama3.2 --base-url http://localhost:11434/v1 --api-key ollama

  # Run with MCP sampling and custom max tokens
  python -m next_gen_ui_mcp --sampling-max-tokens 4096

  # Run with MCP sampling and model preferences
  python -m next_gen_ui_mcp --sampling-hints claude-3-sonnet,claude --sampling-speed-priority 0.8 --sampling-intelligence-priority 0.7

  # Run with SSE transport (for web clients)
  python -m next_gen_ui_mcp --transport sse --host 127.0.0.1 --port 8000

  # Run with streamable-http transport
  python -m next_gen_ui_mcp --transport streamable-http --host 127.0.0.1 --port 8000

  # Run with patternfly component system
  python -m next_gen_ui_mcp --component-system rhds

  # Run with rhds component system via SSE transport
  python -m next_gen_ui_mcp --transport sse --component-system rhds --port 8000
```

As the above examples show you can choose to configure `mcp` sampling, `openai` or `anthropic-vertexai` inference provider.
You have to add the necessary dependencies to your python environment to do so, otherwise the application will complain about them missing.
See detailed documentation below.

Similarly pluggable component systems such as `rhds` also require certain imports, `next_gen_ui_rhds_renderer` in this particular case. 
`json` renderrer is installed by default.

### Configuration Reference

Server can be configured using commandline arguments, or environment variables. CLI has precedence over env variable.

| Commandline Argument          | Environment Variable              | Default Value | Description                                                                                                                           |
| ----------------------------- | --------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `--config-path`               | `NGUI_CONFIG_PATH`                | -             | Path to [YAML configuration files](#yaml-configuration) (to merge more yaml files, multiple commandline args can be used/comma separated in env variable). |
| `--component-system`          | `NGUI_COMPONENT_SYSTEM`           | `json`        | UI Component system (`json` + any installed). Overrides value from YAML config file if used.                                          |
| `--transport`                 | `MCP_TRANSPORT`                   | `stdio`       | Transport protocol for MCP (`stdio`, `sse`, `streamable-http`).                                                                       |
| `--host`                      | `MCP_HOST`                        | `127.0.0.1`   | Host to bind to (for `sse` and `streamable-http` transports).                                                                         |
| `--port`                      | `MCP_PORT`                        | `8000`        | Port to bind to (for `sse` and `streamable-http` transports).                                                                         |
| `--tools`                     | `MCP_TOOLS`                       | -             | List of enabled tools (comma separated). All are enabled by default.                                                                  |
| `--structured_output_enabled` | `MCP_STRUCTURED_OUTPUT_ENABLED`   | `true`        | Enable or disable structured output.                                                                                                  |
| `--provider`                  | `NGUI_PROVIDER`                   | `mcp`         | LLM inference provider (`mcp`, `openai`, `anthropic-vertexai`), for details see below.                                                |
| `--model`                     | `NGUI_MODEL`                      | -             | Model name. Required for other than `mcp` providers.                                                                                  |
| `--base-url`                  | `NGUI_PROVIDER_API_BASE_URL`      | -             | Base URL for API, provider specific defaults. Used by `openai`, `anthropic-vertexai`.                                                 |
| `--api-key`                   | `NGUI_PROVIDER_API_KEY`           | -             | API key for the LLM provider. Used by `openai`, `anthropic-vertexai`.                                                                 |
| `--temperature`               | `NGUI_PROVIDER_TEMPERATURE`       | -             | Temperature for model inference, float value (defaults to `0.0` for deterministic responses). Used by `openai`, `anthropic-vertexai`. |
| `--sampling-max-tokens`       | `NGUI_SAMPLING_MAX_TOKENS`        | -             | Maximum LLM generated tokens, integer value. Used by `mcp` (defaults to `2048`) and `anthropic-vertexai` (defaults to `4096`).        |
| `--sampling-hints`            | `NGUI_SAMPLING_HINTS`             | -             | Comma-separated list of model hint names (e.g., "claude-3-sonnet,claude"). Used by `mcp` provider.                                      |
| `--sampling-cost-priority`   | `NGUI_SAMPLING_COST_PRIORITY`     | -             | Cost priority (0.0-1.0). Higher values prefer cheaper models. Used by `mcp` provider.                                                 |
| `--sampling-speed-priority`  | `NGUI_SAMPLING_SPEED_PRIORITY`    | -             | Speed priority (0.0-1.0). Higher values prefer faster models. Used by `mcp` provider.                                                   |
| `--sampling-intelligence-priority` | `NGUI_SAMPLING_INTELLIGENCE_PRIORITY` | -         | Intelligence priority (0.0-1.0). Higher values prefer more capable models. Used by `mcp` provider.                                       |
| `--anthropic-version`         | `NGUI_PROVIDER_ANTHROPIC_VERSION` | -             | Anthropic version value used in the API call (defaults to `vertex-2023-10-16`). Used by `anthropic-vertexai`.                         |
| `--debug`                     | -                                 |               | Enable debug logging.                                                                                                                 |

### LLM Inference Providers

The Next Gen UI MCP server supports multiple inference providers, controlled by the `--provider` commandline argument / `NGUI_PROVIDER` environment variable:

#### Provider **`mcp`** 

Uses [Model Context Protocol sampling](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling) to leverage the client's LLM capabilities. 
No additional configuration required as it uses the connected MCP client's model, only few optional options are available. 

**MCP client has to support Sampling feature and its optional options!**

Requires:

- `NGUI_SAMPLING_MAX_TOKENS` (optional): Maximum LLM generated tokens, integer value (defaults to `2048`).
- `NGUI_SAMPLING_HINTS` (optional): Comma-separated list of model hint names (e.g., "claude-3-sonnet,claude"). Hints are treated as substrings that can match model names flexibly. Multiple hints are evaluated in order of preference.
- `NGUI_SAMPLING_COST_PRIORITY` (optional): Cost priority value (0.0-1.0). Higher values prefer cheaper models.
- `NGUI_SAMPLING_SPEED_PRIORITY` (optional): Speed priority value (0.0-1.0). Higher values prefer faster models.
- `NGUI_SAMPLING_INTELLIGENCE_PRIORITY` (optional): Intelligence priority value (0.0-1.0). Higher values prefer more capable models.

#### Provider **`openai`**

Uses [LangChain OpenAI inference provider](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/#provides), 
so can be used with any OpenAI compatible APIs, eg. OpenAI API itself,
or [Ollama](https://ollama.com/) for localhost inference,
or [Llama Stack server v0.3.0+](https://llamastack.github.io/docs/api/create-chat-completions).

Requires additional package to be installed:

```sh
"pip install langchain-openai"
```

Requires:

- `NGUI_MODEL`: Model name (e.g., `gpt-4o`, `llama3.2`).
- `NGUI_PROVIDER_API_KEY`: API key for the provider.
- `NGUI_PROVIDER_API_BASE_URL` (optional): Custom base URL for OpenAI-compatible APIs like Ollama or Llama Stack. OpenAI API by default.
- `NGUI_PROVIDER_TEMPERATURE` (optional): Temperature for model inference (defaults to `0.0` for deterministic responses).

Base URL examples:

- OpenAI: `https://api.openai.com/v1` (default)
- Ollama at localhost: `http://localhost:11434/v1`
- Llama Stack server at localhost port `5001` called from MCP server running in image: `http://host.containers.internal:5001/v1`

#### Provider **`anthropic-vertexai`**

Uses [Anthropic/Claude models from proxied Google Vertex AI API endpoint](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/#provides).

Called API url is constructed as `{BASE_URL}/models/{MODEL}:streamRawPredict`. 
API key is sent as `Bearer` token in `Authorization` http request header.

Requires:

  - `NGUI_MODEL`: Model name.
  - `NGUI_PROVIDER_API_BASE_URL`: Base URL of the API.
  - `NGUI_PROVIDER_API_KEY`: API key for the provider.
  - `NGUI_PROVIDER_TEMPERATURE` (optional): Temperature for model inference (defaults to `0.0` for deterministic responses).
  - `NGUI_PROVIDER_ANTHROPIC_VERSION` (optional): Anthropic version to use in API call (defaults to `vertex-2023-10-16`).
  - `NGUI_SAMPLING_MAX_TOKENS` (optional): Maximum LLM generated tokens, integer value (defaults to `4096`).

### YAML configuration

Common [Next Gen UI YAML configuration files](https://redhat-ux.github.io/next-gen-ui-agent/guide/configuration/) can be used to configure UI Agent functionality.

Configuration file extension is available to provide ability to fine-tune descriptions for
the MCP tools and their arguments, to get better performance in your AI assitant/orchestrator.
For details [see `mcp` field in the Schema Definition](https://redhat-ux.github.io/next-gen-ui-agent/spec/mcp/#agent-configuration).

Examle of the mcp yaml configuration extension:

```yaml
mcp:
  tools:
    generate_ui_multiple_components:
      description: Generate multiple UI components for given user_prompt and input data.\nAlways get fresh data from another tool first.
      argument_descriptions:
        user_prompt: "Original user prompt without any changes, so UI components have necessary context. Do not generate this."

# other UI Agent configurations

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

### Testing with MCP Client

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
- `session_id` (str, optional): Session ID. Not used, present just for compatibility purposes.

You can find the input schema in [spec/mcp/generate_ui_input.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/mcp/generate_ui_input.schema.json).

**Returns:**

Object containing:

- UI blocks with rendering and configuration
- Textual summary of the UI Blocks generation

When error occurs during the execution valid ui blocks are rendered. The failing UI Block is mentioned in the summary and don't appear in `blocks` field.

Textual summary is usefull to give the calling LLM a chance to "understand" what happened and react accordingly, include info about UI in natural language response etc.

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
        "content": "{\"component\":\"one-card\",\"image\":\"https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg\",\"id\":\"e5e2db10-de22-4165-889c-02de2f24c901\",\"title\":\"Toy Story Movie Details\",\"fields\":[{\"id\": \"title\",\"name\":\"Title\",\"data_path\":\"$..movie_detail.title\",\"data\":[\"Toy Story\"]},{\"id\": \"year\",\"name\":\"Release Year\",\"data_path\":\"$..movie_detail.year\",\"data\":[1995]},{\"id\": \"imdbRating\",\"name\":\"IMDB Rating\",\"data_path\":\"$..movie_detail.imdbRating\",\"data\":[8.3]},{\"id\": \"runtime\",\"name\":\"Runtime (min)\",\"data_path\":\"$..movie_detail.runtime\",\"data\":[81]},{\"id\": \"plot\",\"name\":\"Plot\",\"data_path\":\"$..movie_detail.plot\",\"data\":[\"A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.\"]}]}"
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
              "id": "title",
              "name": "Title",
              "data_path": "$..movie_detail.title"
            },
            {
              "id": "year",
              "name": "Release Year",
              "data_path": "$..movie_detail.year"
            },
            {
              "id": "imdbRating",
              "name": "IMDB Rating",
              "data_path": "$..movie_detail.imdbRating"
            },
            {
              "id": "runtime",
              "name": "Runtime (min)",
              "data_path": "$..movie_detail.runtime"
            },
            {
              "id": "plot",
              "name": "Plot",
              "data_path": "$..movie_detail.plot"
            },
            {
              "id": "posterUrl",
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
- `session_id` (str, optional): Session ID. Not used, present just for compatibility purposes.

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

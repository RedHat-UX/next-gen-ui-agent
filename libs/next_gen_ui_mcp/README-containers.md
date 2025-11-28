# Next Gen UI MCP Server Container

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Supported-green)](https://github.com/RedHat-UX/next-gen-ui-agent)

[Next Gen UI Agent MCP Server](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/) container image.

## Provides

* container image to easily run [Next Gen UI Agent MCP server](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/)


## Installation

```sh
podman pull quay.io/next-gen-ui/mcp
```

## Usage

### Locally

```sh
podman run --rm -it -p 5100:5100 --env MCP_PORT="5100" \
       --env NGUI_MODEL="llama3.2" --env NGUI_PROVIDER_API_BASE_URL=http://host.containers.internal:11434 --env NGUI_PROVIDER_API_KEY="ollama" \
       quay.io/next-gen-ui/mcp
```

### Openshift

```sh
oc login ...
oc project next-gen-ui # or another
oc apply -f deployment.yaml
```

## Configuration

The MCP server container can be configured via environment variables. All configuration options available to the standalone server are supported.
All env variables are mapped to Next Gen UI MCP server documented in the [MCP Server Guide](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/#server-arguments).

### Environment Variables Reference

| Environment Variable            | Default Value     | Description                                                               |
| ------------------------------- | ----------------- | ------------------------------------------------------------------------- |
| `MCP_TRANSPORT`                 | `streamable-http` | Transport protocol (`stdio`, `sse`, `streamable-http`)                    |
| `MCP_HOST`                      | `0.0.0.0`         | Host to bind to (for HTTP transports)                                     |
| `MCP_PORT`                      | `5000`            | Port to bind to (for HTTP transports)                                     |
| `MCP_TOOLS`                     | `all`             | List of enabled tools (comma separated)                                   |
| `MCP_STRUCTURED_OUTPUT_ENABLED` | `true`            | Enable or disable structured output                                       |
| `NGUI_COMPONENT_SYSTEM`         | `json`            | UI Component system (`json`, `rhds`)                                      |
| `NGUI_PROVIDER`                 | `mcp`             | Inference provider (`mcp`, `openai`, `anthropic-vertexai`)                        |
| `NGUI_MODEL`                    |                   | Model name (required for other than `mcp` providers)                      |
| `NGUI_PROVIDER_API_BASE_URL`    | -                 | Base URL for API, provider specific defaults (for `openai`, `anthropic-vertexai`) |
| `NGUI_PROVIDER_API_KEY`         | -                 | API key for the LLM provider (for `openai`, `anthropic-vertexai`)                 |
| `NGUI_CONFIG_PATH`              | -                 | Path to [Next Gen UI YAML configuration files](https://redhat-ux.github.io/next-gen-ui-agent/guide/configuration/) (comma separated). |


### Providers

The Next Gen UI MCP server supports multiple inference providers, controlled by the `NGUI_PROVIDER` environment variable:

Select the LLM inference provider to use for UI components generation.

#### Provider **`mcp`** 

Uses [Model Context Protocol sampling](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling) to leverage the client's LLM capabilities. 
No additional configuration required as it uses the connected MCP client's model, only few optional options are available. 

**MCP client has to support Sampling feature and its optional options!**

Requires:

- `NGUI_PROVIDER_SAMPLING_MAX_TOKENS` (optional): Maximum LLM generated tokens, integer value (defaults to `2048`).

#### Provider **`openai`**:

Uses [LangChain OpenAI inference provider](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/#provides), 
so can be used with any OpenAI compatible APIs, eg. OpenAI API itself, or [Ollama](https://ollama.com/) for localhost inference, or [Llama Stack server v0.3.0+](https://llamastack.github.io/docs/api/create-chat-completions).

Requires:

- `NGUI_MODEL`: Model name (e.g., `gpt-4o`, `llama3.2`).
- `NGUI_PROVIDER_API_KEY`: API key for the provider.
- `NGUI_PROVIDER_API_BASE_URL` (optional): Custom base URL for OpenAI-compatible APIs like Ollama or Llama Stack. OpenAI API by default.
- `NGUI_PROVIDER_API_TEMPERATURE` (optional): Temperature for model inference (defaults to `0.0` for deterministic responses).

Base URL examples:

- OpenAI: `https://api.openai.com/v1` (default)
- Ollama at localhost: `http://host.containers.internal:11434/v1`
- Llama Stack server at localhost port `5001`: `http://host.containers.internal:5001/v1`

#### Provider **`anthropic-vertexai`**:

Uses [Anthropic/Claude models from proxied Google Vertex AI API endpoint](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/#provides).

Called API url is constructed as `{BASE_URL}/models/{MODEL}:streamRawPredict`. 
API key is sent as `Bearer` token in `Authorization` http request header.

Requires:

  - `NGUI_MODEL`: Model name.
  - `NGUI_PROVIDER_API_BASE_URL`: Base URL of the API.
  - `NGUI_PROVIDER_API_KEY`: API key for the provider.
  - `NGUI_PROVIDER_API_TEMPERATURE` (optional): Temperature for model inference (defaults to `0.0` for deterministic responses).
  - `NGUI_PROVIDER_ANTHROPIC_VERSION` (optional): Anthropic version to use in API call (defaults to `vertex-2023-10-16`).
  - `NGUI_PROVIDER_SAMPLING_MAX_TOKENS` (optional): Maximum LLM generated tokens, integer value (defaults to `4096`).


### Usage Examples

#### Basic Usage with Ollama (Local LLM)
```bash
podman run --rm -it -p 5000:5000 \
    --env MCP_PORT="5000" \
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="llama3.2" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:11434/v1" \
    --env NGUI_PROVIDER_API_KEY="ollama" \
    quay.io/next-gen-ui/mcp
```

#### OpenAI Configuration
```bash
podman run --rm -it -p 5000:5000 \
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="gpt-4o" \
    --env NGUI_PROVIDER_API_KEY="your-openai-api-key" \
    quay.io/next-gen-ui/mcp
```

#### Remote LlamaStack Server Provider
```bash
podman run --rm -it -p 5000:5000 \
    --env NGUI_PROVIDER="llamastack" \
    --env NGUI_MODEL="llama3.2-3b" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:5001" \
    quay.io/next-gen-ui/mcp
```

#### Configuration Using Environment File
Create a `.env` file:
```bash
# .env file
MCP_PORT=5000
MCP_HOST=0.0.0.0
MCP_TRANSPORT=streamable-http
MCP_STRUCTURED_OUTPUT_ENABLED="false"
NGUI_COMPONENT_SYSTEM=json
NGUI_PROVIDER=openai
NGUI_MODEL=gpt-4o
NGUI_PROVIDER_API_KEY=your-api-key-here
```

Run with environment file:
```bash
podman run --rm -it -p 5000:5000 --env-file .env quay.io/next-gen-ui/mcp
```

### Network Configuration

For local development connecting to services running on the host machine:

- Use `host.containers.internal` to access host services (works with Podman and Docker Desktop)
- For Linux with Podman, you may need to use `host.docker.internal` or the host's IP address
- Ensure the target services (like Ollama) are accessible from containers

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-container/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_mcp)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)

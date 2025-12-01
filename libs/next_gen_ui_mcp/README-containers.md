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

The MCP server container can be configured via environment variables. 
For available env variables and their meaning see [MCP Server Guide](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/#server-arguments).

Dependencien necessary for `openai` inference provider are installed in the image.

`rhds` renderer is not installed in this image, create sub-image with it if required.

**Default values are changed for some configurations in the image!**

| Environment Variable | Default Value     | Description                                                |
| ---------------------| ----------------- | -----------------------------------------------------------|
| `MCP_TRANSPORT`      | `streamable-http` | Transport protocol (`stdio`, `sse`, `streamable-http`)     |
| `MCP_HOST`           | `0.0.0.0`         | Host to bind to (for HTTP transports)                      |
| `MCP_PORT`           | `5000`            | Port to bind to (for HTTP transports)                      |
| `NGUI_PROVIDER`      | `openai`          | Inference provider (`mcp`, `openai`, `anthropic-vertexai`) |


### Usage Examples

#### Basic Usage with Ollama (Local LLM)

Use `http://host.containers.internal:11434/v1` url to reffer system the immage is running in:

```bash
podman run --rm -it -p 5000:5000 \
    --env MCP_PORT="5000" \
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="llama3.2" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:11434/v1" \
    --env NGUI_PROVIDER_API_KEY="ollama" \
    quay.io/next-gen-ui/mcp
```

#### OpenAI API Configuration
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
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="llama3.2-3b" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:5001/v1" \
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

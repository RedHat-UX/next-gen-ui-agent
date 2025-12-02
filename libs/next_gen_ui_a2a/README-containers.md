# Next Gen UI Agent A2A Server Container

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

[![Module Category](https://img.shields.io/badge/Module%20Category-AI%20Protocol-red)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)


## Provides

* container image to easily run [Next Gen UI Agent A2A Server](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/a2a-library/)

## Installation

```sh
podman pull quay.io/next-gen-ui/a2a
```

## Usage

```sh
podman run --rm -p 9999:9999 \
    -e INFERENCE_MODEL=llama3.2 \
    -e OPEN_API_URL=http://host.containers.internal:11434/v1 \
    quay.io/next-gen-ui/a2a:dev
```

## Configuration

The A2A Server container can be configured via environment variables. 
For available env variables and their meaning see [A2A Server Guide](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/a2a-library/#configuration-reference).

Dependencien necessary for `openai` inference provider are installed in the image.

**Default values are changed for some configurations in the image!**

| Environment Variable | Default Value     | Description                                                |
| ---------------------| ----------------- | -----------------------------------------------------------|
| `MCP_HOST`           | `0.0.0.0`         | Host to bind to (for HTTP transports)                      |
| `MCP_PORT`           | `9999`            | Port to bind to (for HTTP transports)                      |
| `NGUI_MODEL`         | `gpt-4o`          | Model name                                                 |

### Usage Examples

#### Basic Usage with Ollama (Local LLM)

```bash
podman run --rm -it -p 5000:5000 \
    --env MCP_PORT="5000" \
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="llama3.2" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:11434/v1" \
    --env NGUI_PROVIDER_API_KEY="ollama" \
    quay.io/next-gen-ui/a2a
```

#### OpenAI API Configuration

```bash
podman run --rm -it -p 5000:5000 \
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="gpt-4o" \
    --env NGUI_PROVIDER_API_KEY="your-openai-api-key" \
    quay.io/next-gen-ui/a2a
```

#### Remote LlamaStack Server

```bash
podman run --rm -it -p 5000:5000 \
    --env NGUI_PROVIDER="openai" \
    --env NGUI_MODEL="llama3.2-3b" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:5001/v1" \
    quay.io/next-gen-ui/a2a
```

#### Configuration Using Environment File

Create a `.env` file:

```bash
# .env file
A2A_PORT=5000
A2A_HOST=0.0.0.0
NGUI_COMPONENT_SYSTEM=json
NGUI_PROVIDER=openai
NGUI_MODEL=gpt-4o
NGUI_PROVIDER_API_KEY=your-api-key-here
```

Run with environment file:
```bash
podman run --rm -it -p 5000:5000 --env-file .env quay.io/next-gen-ui/a2a
```

### Network Configuration

For local development connecting to services running on the host machine:

- Use `host.containers.internal` to access host services (works with Podman and Docker Desktop)
- For Linux with Podman, you may need to use `host.docker.internal` or the host's IP address
- Ensure the target services (like Ollama) are accessible from containers

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/a2a-container/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_a2a)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)

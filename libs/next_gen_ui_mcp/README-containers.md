# Next Gen UI MCP Server Container

Next Gen UI MCP Server container image.

For more information visit [GitHub](https://github.com/RedHat-UX/next-gen-ui-agent).

```sh
podman pull quay.io/next-gen-ui/mcp
```

## Usage

```sh
podman run --rm -it -p 5100:5100 --env MCP_PORT="5100" \
       --env NGUI_MODEL="llama3.2" --env NGUI_PROVIDER_API_BASE_URL=http://host.containers.internal:11434 --env NGUI_PROVIDER_API_KEY="ollama" \
       quay.io/next-gen-ui/mcp
```

## Configuration

The MCP server container can be configured via environment variables. All configuration options available to the standalone server are supported.

### Environment Variables Reference

| Environment Variable         | Default Value     | Description                                            |
| ---------------------------- | ----------------- | ------------------------------------------------------ |
| `MCP_TRANSPORT`              | `streamable-http` | Transport protocol (`stdio`, `sse`, `streamable-http`) |
| `MCP_HOST`                   | `0.0.0.0`         | Host to bind to (for HTTP transports)                  |
| `MCP_PORT`                   | `5000`            | Port to bind to (for HTTP transports)                  |
| `NGUI_COMPONENT_SYSTEM`      | `json`            | Component system (`json`, `rhds`)                      |
| `NGUI_PROVIDER`              | `langchain`       | Inference provider (`mcp`, `llamastack`, `langchain`)  |
| `NGUI_MODEL`                 | `gpt-4o`          | Model name (required for non-MCP providers)            |
| `NGUI_PROVIDER_API_BASE_URL` | -                 | Base URL for OpenAI-compatible API                     |
| `NGUI_PROVIDER_API_KEY`      | -                 | API key for the LLM provider                           |
| `NGUI_PROVIDER_LLAMA_URL`    | -                 | LlamaStack server URL (if `llamastack` is used)         |

### Providers

The Next Gen UI MCP server supports three inference providers, controlled by the `NGUI_PROVIDER` environment variable:

Selects the inference provider to use for generating UI components:

#### Provider **`mcp`** 

Uses Model Context Protocol sampling to leverage the client's LLM capabilities. No additional configuration required as it uses the connected MCP client's model.

#### Provider **`langchain`**:

Uses LangChain with OpenAI-compatible APIs.

Requires:

- `NGUI_MODEL`: Model name (e.g., `gpt-4o`, `llama3.2`)
- `NGUI_PROVIDER_API_KEY`: API key for the provider
- `NGUI_PROVIDER_API_BASE_URL` (optional): Custom base URL for OpenAI-compatible APIs like Ollama

Examples:

- OpenAI: `https://api.openai.com/v1` (default)
- Ollama: `http://host.containers.internal:11434/v1`

#### Provider **`llamastack`**:

Uses LlamaStack server for inference.

Requires:

  - `NGUI_MODEL`: Model name available on the LlamaStack server
  - `NGUI_PROVIDER_LLAMA_URL`: URL of the LlamaStack server


### Usage Examples

#### Basic Usage with Ollama (Local LLM)
```bash
podman run --rm -it -p 5000:5000 \
    --env MCP_PORT="5000" \
    --env NGUI_MODEL="llama3.2" \
    --env NGUI_PROVIDER_API_BASE_URL="http://host.containers.internal:11434/v1" \
    --env NGUI_PROVIDER_API_KEY="ollama" \
    quay.io/next-gen-ui/mcp
```

#### OpenAI Configuration
```bash
podman run --rm -it -p 5000:5000 \
    --env NGUI_MODEL="gpt-4o" \
    --env NGUI_PROVIDER_API_KEY="your-openai-api-key" \
    quay.io/next-gen-ui/mcp
```

#### Using with Environment File
Create a `.env` file:
```bash
# .env file
MCP_PORT=5000
MCP_HOST=0.0.0.0
MCP_TRANSPORT=streamable-http
NGUI_COMPONENT_SYSTEM=json
NGUI_PROVIDER=langchain
NGUI_MODEL=gpt-4o
NGUI_PROVIDER_API_KEY=your-api-key-here
```

Run with environment file:
```bash
podman run --rm -it -p 5000:5000 --env-file .env quay.io/next-gen-ui/mcp
```

#### LlamaStack Provider
```bash
podman run --rm -it -p 5000:5000 \
    --env NGUI_PROVIDER="llamastack" \
    --env NGUI_MODEL="llama3.2-3b" \
    --env NGUI_PROVIDER_LLAMA_URL="http://host.containers.internal:5001" \
    quay.io/next-gen-ui/mcp
```

### Network Configuration

For local development connecting to services running on the host machine:

- Use `host.containers.internal` to access host services (works with Podman and Docker Desktop)
- For Linux with Podman, you may need to use `host.docker.internal` or the host's IP address
- Ensure the target services (like Ollama) are accessible from containers

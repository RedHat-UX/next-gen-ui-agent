# Next Gen UI MCP Server

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

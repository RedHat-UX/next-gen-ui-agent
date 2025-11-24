# MCP Server Spec

Specifications of the json format (as JSON Schema) of the [Next Gen UI MCP Server](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/).
Mainly usefull to implement client-side interaction directly with MCP server.

How relevant object types are generated to TypeScript then can be tested here: [https://transform.tools/json-schema-to-typescript](https://transform.tools/json-schema-to-typescript)

## Generate UI

### Input

2 inputs required: `user_prompt` and `input_data`.

Example JSON input for `input_data` argument:
```json
[
  {
    "data": "some-data",
    "id": "id",
    "type": "pods_log"
  }
]
```


### Response
[mcp/generate_ui_output.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/mcp/generate_ui_output.schema.json)

Example JSON output:
```json
{
  "blocks": [
    {
      "id": "tool_call_id",
      "rendering": {
        "id": "tool_call_id",
        "component_system": "json",
        "mime_type": "application/json",
        "content": "{\"id\":\"id\",\"data\":\"some-data\",\"component\":\"log\"}"
      }
    }
  ],
  "summary": "Components are rendered in UI.\nCount: 1\n1. type: log"
}
```

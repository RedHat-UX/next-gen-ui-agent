# MCP Server Spec

Specifications of the json format (as JSON Schema) of the [Next Gen UI MCP Server](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/mcp-library/).
Mainly usefull to implement client-side interaction directly with MCP server.

How relevant object types are generated to TypeScript then can be tested here: [https://transform.tools/json-schema-to-typescript](https://transform.tools/json-schema-to-typescript)

## Generate UI

### Input for `generate_ui_multiple_components` tool

[mcp/generate_ui_input.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/mcp/generate_ui_input.schema.json)

Example JSON input for `input_data` argument:

```json
{
  "user_prompt": "",
  "input_data": [
    {
      "data": "some-data",
      "id": "id",
      "type": "pods_log"
    }
  ]
}
```


### Response from `generate_ui_multiple_components` and `generate_ui_component` tools

[mcp/generate_ui_output.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/mcp/generate_ui_output.schema.json)

Example JSON output:
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

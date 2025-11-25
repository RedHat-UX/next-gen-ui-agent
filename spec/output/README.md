# UI Agent Output Spec

[UI Agent core output JSON Schema is available here](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/output/ui_block.schema.json). 
It is produced by the [Next Gen UI Agent core](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/), but is used as part of the output of distinct AI framework/protocol bindings also.

Besides UI component rendering, it also contains structured UI component configuration, which can be used by the *Controlling assistant* GUI/Frontend for advanced UI features, like live data updates from backend, manual selection of visualized fields etc. 
See `UIBlockConfiguration` and `UIBlockComponentMetadata` parts.

Example for the `json` rendering, `table` component with `generate_all_fields` enabled:

```json
{
    "id": "e5e2db10-de22-4165-889c-02de2f24c901",
    "rendering": {
        "id": "e5e2db10-de22-4165-889c-02de2f24c901",
        "component_system": "json",
        "mime_type": "application/json",
        "content": "{\"component\":\"table\",\"id\":\"e5e2db10-de22-4165-889c-02de2f24c901\",\"title\":\"Movies\",\"fields\":[{\"id\": \"title\",\"name\":\"Title\",\"data_path\":\"$..movies[*].title\",\"data\":[\"Toy Story\"]},{\"id\": \"year\",\"name\":\"Release Year\",\"data_path\":\"$..movies[*].year\",\"data\":[1995]},{\"id\": \"imdbRating\",\"name\":\"IMDB Rating\",\"data_path\":\"$..movies[*].imdbRating\",\"data\":[8.3]}]}"
    },
    "configuration": {
        "data_type": "movies",
        "input_data_transformer_name": "json",
        "json_wrapping_field_name": "movies",
        "component_metadata": {
            "id": "e5e2db10-de22-4165-889c-02de2f24c901",
            "title": "Movies",
            "component": "table",
            "fields": [
                {
                    "id": "title",
                    "name": "Title",
                    "data_path": "$..movies[*].title"
                },
                {
                    "id": "year",
                    "name": "Release Year",
                    "data_path": "$..movies[*].year"
                },
                {
                    "id": "imdbRating",
                    "name": "IMDB Rating",
                    "data_path": "$..movies[*].imdbRating"
                }
            ],
            "fields_all": [
                {
                    "id": "title",
                    "name": "Title",
                    "data_path": "$..movies[*].title"
                },
                {
                    "id": "year",
                    "name": "Release Year",
                    "data_path": "$..movies[*].year"
                },
                {
                    "id": "plot",
                    "name": "Plot",
                    "data_path": "$..movies[*].plot"
                },
                {
                    "id": "imdbRating",
                    "name": "Imdb Rating",
                    "data_path": "$..movies[*].imdbRating"
                },
                {
                    "id": "revenue",
                    "name": "Revenue",
                    "data_path": "$..movies[*].revenue"
                },
            ]
        }
    }
}
```
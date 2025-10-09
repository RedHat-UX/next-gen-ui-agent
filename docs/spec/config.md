# Agent Configuration Spec

[UI Agent Configuration JSON Schema is available here](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/config/agent_config.schema.json).

It can be used to validate [agent configuration YAML files](../guide/configuration.md#from-yaml-string).

To use yaml configuration file auto completion or validation in your favorite IDE/editor, you can configure it, see next chapters.

## Multiple IDEs - from JSON Schema Store

The schema is published in [JSON Schema Store](https://www.schemastore.org/) and its [JSON API catalog](https://www.schemastore.org/api/json/catalog.json). 

It is bound to `ngui_*.yaml`, `ngui_*.yml` and `ngui_*.json` file patterns. So it is automatically used in [supporting IDEs/editors](https://www.schemastore.org/#editors) 
regarding their default configuration.

## VS Code or Cursor

You need extension with YAML language support, eg. [Red Hat provided `YAML` extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).

For this extension, [`JSON Schema Store`](#multiple-ides---from-json-schema-store) is used by default, so the schema is immediatelly available. 
It is bound to that file patterns, or can be autodetected/selected for other files.

You can also configure binding to other filenames by adding next section to your `settings.json` (it 
can be accessed using menu `File` > `Preferences` > `Settings` > `Extensions` > `YAML` > `Schemas`):

```json
"yaml.schemas": {
    "https://raw.githubusercontent.com/RedHat-UX/next-gen-ui-agent/refs/heads/main/spec/config/agent_config.schema.json": ["ui_agent_config.yaml"]
},
```


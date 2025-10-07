# Agent Configuration Spec

[UI Agent Configuration JSON Schema is available here](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/config/agent_config.schema.json).

It can be used to validate [agent configuration YAML files](../guide/configuration.md#from-yaml-string).

## VS Code

Add next section to your `settings.json` to :

```json
"yaml.schemas": {
    "https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/config/agent_config.schema.json": ["ngui_*.yaml", "ngui_*.yml"]
},
```


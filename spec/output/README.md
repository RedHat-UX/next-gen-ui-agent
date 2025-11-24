# UI Agent Output Spec

[UI Agent core output JSON Schema is available here](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/output/ui_block.schema.json). 
It is produced by the [Next Gen UI Agent core](https://redhat-ux.github.io/next-gen-ui-agent/guide/ai_apps_binding/pythonlib/), but is used as part of the output of distinct AI framework/protocol bindings also.

Besides UI component rendering, it also contains structured UI component configuration, which can be used by the *Controlling assistant* GUI/Frontend for advanced UI features, like live data updates from backend, manual selection of visualized fields etc. 
See `UIBlockConfiguration` and `UIBlockComponentMetadata` parts.

How relevant object types are generated to TypeScript then can be tested here: [https://transform.tools/json-schema-to-typescript](https://transform.tools/json-schema-to-typescript)


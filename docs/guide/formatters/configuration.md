# Customizing Component Fields with Formatters

This guide explains how to customize component fields (table columns, card fields, etc.) with formatters in Next Gen UI Agent.

## Overview

Formatters are functions registered in your frontend that transform raw data values into formatted UI elements. They work across all component types: table columns, card fields, chart labels, and more. The agent automatically extracts data keys from field paths (e.g., `$.pods[*].cpu_usage` → `cpu_usage`) and uses them as formatter IDs, so you typically don't need explicit configuration for common fields.

## Setup

### 1. Configure Backend

Configure formatter mappings in `AgentConfig`. Only override fields when the formatter ID differs from the data key. Overrides are matched against data keys (extracted from `data_path`), not field names.

**Matching Priority:**
1. Exact match (case-sensitive)
2. Case-insensitive match
3. Pattern match (wildcard patterns)
4. Auto-detect (use data key as formatter ID)

```python
from next_gen_ui_agent import AgentConfig
from next_gen_ui_agent.types import AgentConfigDataType

config = AgentConfig(
    data_types={
        "getPods": AgentConfigDataType(
            formatter_overrides={"created": "date"},  # Data key "created" -> formatter "date"
            on_row_click="onRowClick"
        ),
        "getNodes": AgentConfigDataType(
            formatter_overrides={
                "status": "node_status",  # Data key "status" -> formatter "node_status"
                "cpu": "cpu_usage",  # Data key "cpu" -> formatter "cpu_usage"
                "memory": "memory_usage",  # Data key "memory" -> formatter "memory_usage"
                "version": "version_label"  # Data key "version" -> formatter "version_label"
            },
            on_row_click="onRowClick"
        ),
        "cluster_info": AgentConfigDataType(
            formatter_overrides={
                "status": "cluster_info.status",
                "last_backup": "date",
                "*url*": "url",  # Pattern: matches any key containing "url" (e.g., "url", "api_url", "monitoring_dashboard_url")
                "*_usage*": "percentage",  # Pattern: matches keys containing "_usage" (e.g., "cpu_usage", "memory_usage")
            },
        ),
    }
)
```

### Pattern Matching

You can use wildcard patterns in `formatter_overrides` to match multiple data keys with a single rule:

- `"*url*"` - Matches any key containing "url" (e.g., `url`, `api_url`, `monitoring_dashboard_url`)
- `"url*"` - Matches keys starting with "url" (e.g., `url`, `url_path`, `url_base`)
- `"*url"` - Matches keys ending with "url" (e.g., `url`, `api_url`, `dashboard_url`)

Pattern matching is case-insensitive and checked after exact and case-insensitive matches. This is useful when multiple fields should use the same formatter without listing each one explicitly.

**Key point**: `data_types` key must match `InputData.type`.

### 2. Set InputData.type

The `InputData.type` must match a key in your `AgentConfig.data_types`. It can be any identifier.

**With Framework Bindings** (automatic):
Most framework bindings automatically map tool names to `InputData.type`:

**LangGraph:**
```python
from next_gen_ui_langgraph import NextGenUILangGraphAgent

@tool
def getPods():
    return json.dumps({"pods": pods_result})
# Tool name "getPods" automatically becomes InputData.type
```

**LlamaStack:**
```python
from next_gen_ui_llama_stack import NextGenUILlamaStackAgent

# ToolResponse.tool_name automatically becomes InputData.type
```

**With Core Agent** (manual):
When using `NextGenUIAgent` directly, create `InputData` manually:

```python
from next_gen_ui_agent import NextGenUIAgent, InputData

input_data = InputData(
    id="request_123",
    data=json.dumps({"pods": pods_result}),
    type="getPods"  # Must match config key
)
```

### 3. Register Formatters in Frontend

Register formatters using `ComponentHandlerRegistry`. Resolution priority: data-type specific → generic fallback.

```typescript
import { ComponentHandlerRegistryProvider, useComponentHandlerRegistry } from '@rhngui/patternfly-react-renderer';
import { Label } from '@patternfly/react-core';

function YourApp() {
  const registry = useComponentHandlerRegistry();

  useEffect(() => {
    // Generic formatters (auto-detected from data keys)
    registry.registerFormatter('status', (value) => <Label>{value}</Label>);
    registry.registerFormatter('name', (value) => <strong>{value}</strong>);
    registry.registerFormatter('cpu_usage', (value) => `${(parseFloat(String(value)) * 100).toFixed(1)}%`);
    registry.registerFormatter('date', (value) => new Date(value).toLocaleDateString());

    // Data-type specific (optional)
    registry.registerFormatter('getPods.status', (value) => <Label color="green">{value}</Label>);

    // Row click handlers
    registry.registerOnRowClick('onRowClick', (event, rowData) => {
      window.alert(`Clicked: ${rowData.name}`);
    });
  }, [registry]);
}
```

## How It Works

1. Backend creates `InputData` with `data` and `type`
2. Agent uses `type` to look up config in `AgentConfig.data_types`
3. Agent applies formatters (in priority order):
   - Extracts data key from field's `data_path` (e.g., `$.pods[*].cpu_usage` → `cpu_usage`)
   - Checks `formatter_overrides` for exact match (case-sensitive)
   - If no match, checks case-insensitive match
   - If no match, checks wildcard patterns (`*url*`, `url*`, `*url`)
   - If no override found, uses the data key as the formatter ID (auto-detect)
4. Frontend resolves: `{type}.{formatter_id}` → `{formatter_id}` (fallback)

## Row Click Handlers (Optional)

Enable interactive row clicks that trigger actions:

```typescript
registry.registerOnRowClick('onRowClick', (event, rowData) => {
  event.preventDefault();
  // Trigger new prompt, show modal, navigate, etc.
  handleSend(`Show details for ${rowData.name}`);
});
```

## Best Practices

- Only use `formatter_overrides` when formatter ID differs from the data key
- Register formatters at app initialization
- Keep `InputData.type` consistent between backend and frontend

## Troubleshooting

- **Formatters not applied?** Verify `InputData.type` matches `AgentConfig.data_types` key
- **Not rendering?** Ensure `ComponentHandlerRegistryProvider` wraps your app
- **Wrong formatter?** Check resolution priority (data-type specific > generic)

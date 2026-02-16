---
name: Configurable MCP Argument Exclusion
overview: Add YAML configuration to control which arguments are excluded from MCP tool schemas, with session_id always excluded by default and ability to add more exclusions per tool.
todos:
  - id: add-config-field
    content: Add schema_excluded_args field to MCPAgentToolConfig in agent_config.py
    status: completed
  - id: add-helper-method
    content: Add _get_excluded_args helper method in agent.py
    status: completed
  - id: update-decorators
    content: Update both @self.mcp.tool decorators to use _get_excluded_args
    status: completed
  - id: write-tests
    content: Write comprehensive tests for schema exclusion functionality
    status: completed
  - id: update-docs
    content: Update README.md with schema_excluded_args documentation
    status: completed
  - id: run-tests
    content: Run all tests using pants to verify implementation
    status: completed
isProject: false
---

# Configurable MCP Tool Argument Exclusion

## Overview

Implement configurable argument exclusion for MCP tools via YAML, allowing users to exclude specific arguments from the MCP schema while keeping `session_id` always excluded.

## Implementation Steps

### 1. Update Configuration Schema

**File:** `[libs/next_gen_ui_mcp/agent_config.py](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/agent_config.py)`

Add new field to `MCPAgentToolConfig` class:

```python
schema_excluded_args: Optional[List[str]] = Field(
    description="List of argument names to exclude from the MCP tool schema. 'session_id' is always excluded by default. Additional arguments listed here will be added to the exclusion list.",
    default=None,
)
```

This follows the same pattern as existing fields like `argument_descriptions`.

### 2. Add Helper Method for Excluded Args

**File:** `[libs/next_gen_ui_mcp/agent.py](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/agent.py)`

Add method after `_get_argument_description` (around line 251):

```python
def _get_excluded_args(
    self,
    tool_config: Optional[MCPAgentToolConfig],
) -> List[str]:
    """Get list of arguments to exclude from MCP schema.
    
    Args:
        tool_config: The tool config object
        
    Returns:
        List of argument names to exclude (always includes 'session_id')
    """
    # session_id is always excluded
    excluded = ["session_id"]
    
    # Add any additional exclusions from config
    if tool_config and tool_config.schema_excluded_args:
        excluded.extend(tool_config.schema_excluded_args)
    
    return excluded
```

### 3. Update Tool Decorators

**For `generate_ui_component**` (line 266):

- Replace hardcoded `exclude_args=["session_id"]` with `exclude_args=self._get_excluded_args(tool_config)`

**For `generate_ui_multiple_components**` (line 384):

- Replace commented `# exclude_args=["structured_data"],` with `exclude_args=self._get_excluded_args(tool_config_multiple)`

### 4. Write Tests

**File:** `[libs/next_gen_ui_mcp/agent_test.py](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/agent_test.py)`

Add new test class or add tests to existing `TestToolConfiguration` class:

- **Test 1: Default behavior** - Verify `session_id` is excluded by default when no config is provided
- **Test 2: Additional exclusions** - Verify adding `structured_data` to exclusions for `generate_ui_multiple_components`
- **Test 3: Both tools** - Test exclusions work independently for both tools
- **Test 4: Verify schema** - Use `client.list_tools()` to verify excluded args don't appear in `inputSchema["properties"]`

Example test structure:

```python
async def test_schema_excluded_args_default():
    # Verify session_id is excluded by default
    ngui_agent = NextGenUIMCPServer(config=MCPAgentConfig(component_system="json"))
    async with Client(ngui_agent.get_mcp_server()) as client:
        tools = await client.list_tools()
    tool = next(t for t in tools if t.name == "generate_ui_component")
    assert "session_id" not in tool.inputSchema["properties"]
```

### 5. Update Documentation

**File:** `[libs/next_gen_ui_mcp/README.md](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/README.md)`

Add to YAML configuration section (around line 179, after the existing example):

```yaml
### Schema Argument Exclusion

You can configure which arguments are excluded from the MCP tool schema. The `session_id` argument is always excluded by default. Additional arguments can be specified using `schema_excluded_args`:

```yaml
mcp:
  tools:
    generate_ui_multiple_components:
      schema_excluded_args:
        - structured_data  # Exclude this argument from schema
    generate_ui_component:
      schema_excluded_args:
        - data_type_metadata  # Exclude this argument from schema
```

**Note:** The `session_id` argument is always excluded regardless of configuration and does not need to be listed.

```

## Testing Strategy

1. Run existing tests to ensure no regressions
2. Add new tests for the exclusion functionality
3. Test with sample YAML configuration
4. Verify excluded args don't appear in MCP tool schema via `list_tools()`

## Key Files to Modify

- `[libs/next_gen_ui_mcp/agent_config.py](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/agent_config.py)` - Add config field
- `[libs/next_gen_ui_mcp/agent.py](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/agent.py)` - Add helper method and update decorators
- `[libs/next_gen_ui_mcp/agent_test.py](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/agent_test.py)` - Add tests
- `[libs/next_gen_ui_mcp/README.md](/home/velias/Devel/projects/next-gen-ui/next-gen-ui-agent/libs/next_gen_ui_mcp/README.md)` - Add documentation
```


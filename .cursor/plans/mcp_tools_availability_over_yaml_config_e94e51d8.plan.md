---
name: MCP Tool YAML Config
overview: Add YAML configuration support for enabling/disabling MCP tools per-tool basis, maintaining CLI/env variable precedence over YAML config, with comprehensive tests and documentation.
todos:
  - id: extend-config-schema
    content: "Add `enabled: Optional[bool]` field to `MCPAgentToolConfig` in agent_config.py"
    status: completed
  - id: implement-precedence
    content: Update `NextGenUIMCPServer.__init__()` to implement 3-level precedence (CLI/env > YAML > default)
    status: completed
  - id: write-tests
    content: Add comprehensive tests in agent_test.py covering YAML config, precedence, and default behavior
    status: completed
  - id: update-readme
    content: Document YAML `enabled` field and precedence rules in README.md with examples
    status: completed
isProject: false
---

# MCP Tool YAML Configuration Implementation

## Overview

Implement YAML configuration support for enabling/disabling individual MCP tools while maintaining proper precedence: **CLI/env > YAML > default (all enabled)**.

## Current State

The codebase already has:

- **Tool control via CLI/env**: `--tools` / `MCP_TOOLS` specifies list of enabled tools
- **MCP config structure**: `MCPAgentConfig` extends `AgentConfig` with `mcp.tools` for per-tool overrides (currently only `description` and `argument_descriptions`)
- **Tool registration**: `NextGenUIMCPServer._setup_mcp_tools()` registers tools with `enabled=` flag based on `self.enabled_tools` list

```162:165:libs/next_gen_ui_mcp/agent.py
MCP_ALL_TOOLS = [
    "generate_ui_component",
    "generate_ui_multiple_components",
]
```

```198:206:libs/next_gen_ui_mcp/agent.py
        if enabled_tools:
            for t in enabled_tools:
                if t not in MCP_ALL_TOOLS:
                    raise ValueError(
                        f"tool '{t}' is no valid. Available tools are: {MCP_ALL_TOOLS}"
                    )
            self.enabled_tools = enabled_tools
        else:
            self.enabled_tools = MCP_ALL_TOOLS
```

## Implementation Steps

### 1. Extend Configuration Schema

**File**: `[libs/next_gen_ui_mcp/agent_config.py](libs/next_gen_ui_mcp/agent_config.py)`

Add `enabled` field to `MCPAgentToolConfig`:

```python
class MCPAgentToolConfig(BaseModel):
    """Information to override default values in the MCP Agent tool."""

    enabled: Optional[bool] = Field(
        description="Whether the tool is enabled. Defaults to True.",
        default=None,
    )
    
    description: Optional[str] = Field(...)
    argument_descriptions: Optional[dict[str, str]] = Field(...)
```

### 2. Implement Precedence Logic

**File**: `[libs/next_gen_ui_mcp/agent.py](libs/next_gen_ui_mcp/agent.py)`

Update `NextGenUIMCPServer.__init__()` to merge configurations with precedence:

**Current logic** (lines 198-206):

- If `enabled_tools` parameter is provided → use it
- Otherwise → use `MCP_ALL_TOOLS`

**New logic** should:

1. Start with default: all tools enabled
2. Apply YAML config: disable tools where `config.mcp.tools.<tool>.enabled = False`
3. Apply CLI/env override: if `enabled_tools` parameter provided, use it (ignore YAML)
4. Validate all tool names

**Example implementation**:

```python
# In __init__ around line 198
if enabled_tools:
    # CLI/env has highest precedence
    for t in enabled_tools:
        if t not in MCP_ALL_TOOLS:
            raise ValueError(f"tool '{t}' is not valid. Available tools are: {MCP_ALL_TOOLS}")
    self.enabled_tools = enabled_tools
else:
    # Start with all tools enabled
    self.enabled_tools = list(MCP_ALL_TOOLS)
    
    # Apply YAML config if present
    if self.config.mcp and self.config.mcp.tools:
        tools_config = self.config.mcp.tools
        for tool_name in MCP_ALL_TOOLS:
            tool_config = getattr(tools_config, tool_name, None)
            if tool_config and tool_config.enabled is False:
                if tool_name in self.enabled_tools:
                    self.enabled_tools.remove(tool_name)
```

### 3. Write Tests

**File**: `[libs/next_gen_ui_mcp/agent_test.py](libs/next_gen_ui_mcp/agent_test.py)`

Add comprehensive test cases:

#### Test 3.1: YAML config enables/disables tools

- Create config with `mcp.tools.generate_ui_component.enabled: false`
- Initialize `NextGenUIMCPServer` with config (no `enabled_tools` param)
- Verify `generate_ui_component` is disabled, `generate_ui_multiple_components` is enabled

#### Test 3.2: CLI/env precedence over YAML

- Create config with `mcp.tools.generate_ui_component.enabled: false`
- Initialize with `enabled_tools=["generate_ui_component"]`
- Verify `generate_ui_component` is enabled (CLI overrides YAML)

#### Test 3.3: Default behavior (all enabled)

- Initialize with no config and no `enabled_tools`
- Verify all tools are enabled

#### Test 3.4: YAML enables subset of tools

- Create config with both tools having explicit `enabled: true/false`
- Verify correct tools are enabled

#### Test 3.5: Verify tool actually works/doesn't work

- Test that disabled tool is not listed in MCP server tools
- Test that enabled tool can be called successfully

**Testing approach**: Use pytest fixtures and existing patterns from `agent_test.py`

### 4. Update Documentation

**File**: `[libs/next_gen_ui_mcp/README.md](libs/next_gen_ui_mcp/README.md)`

#### Update section "Configuration Reference" (line ~90)

Add row for YAML config path reference

#### Update section "YAML configuration" (line ~170)

Expand the example (line 178-190) to include `enabled` field:

```yaml
mcp:
  tools:
    generate_ui_component:
      enabled: false  # Disable this tool (default: true)
    generate_ui_multiple_components:
      description: Generate multiple UI components for given user_prompt and input data.\nAlways get fresh data from another tool first.
      enabled: true  # Explicitly enable (optional, default is true)
      argument_descriptions:
        user_prompt: "Original user prompt without any changes, so UI components have necessary context. Do not generate this."
```

Add explanation of precedence:

```markdown
**Tool Enabling/Disabling Precedence:**

1. **CLI/Environment** (highest): `--tools` / `MCP_TOOLS` - when specified, overrides YAML
2. **YAML Configuration**: `mcp.tools.<tool_name>.enabled` - controls per-tool enablement
3. **Default** (lowest): All tools enabled

Examples:
- YAML disables `generate_ui_component`, no CLI arg → tool is disabled
- YAML disables `generate_ui_component`, CLI `--tools generate_ui_component` → tool is enabled (CLI wins)
- No YAML, no CLI → all tools enabled (default)
```

## Files to Modify

1. `[libs/next_gen_ui_mcp/agent_config.py](libs/next_gen_ui_mcp/agent_config.py)` - Add `enabled` field
2. `[libs/next_gen_ui_mcp/agent.py](libs/next_gen_ui_mcp/agent.py)` - Implement precedence logic in `__init__`
3. `[libs/next_gen_ui_mcp/agent_test.py](libs/next_gen_ui_mcp/agent_test.py)` - Add comprehensive tests
4. `[libs/next_gen_ui_mcp/README.md](libs/next_gen_ui_mcp/README.md)` - Update documentation

## Validation

- All tests pass: `pants test libs/next_gen_ui_mcp::`
- Format/lint clean: Run pants format check skill
- Existing functionality unchanged when no YAML config used
- CLI/env variables maintain backward compatibility


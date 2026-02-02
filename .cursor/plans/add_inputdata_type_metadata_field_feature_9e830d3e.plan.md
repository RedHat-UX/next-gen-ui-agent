---
name: Add InputData.type_metadata Field Feature
overview: Add optional `type_metadata` field to InputData that gets passed through to UIBlockConfiguration as `data_type_metadata`, enabling tool call arguments to be preserved for frontend data refresh operations.
todos:
  - id: types
    content: Add type_metadata to InputData and data_type_metadata to UIBlockConfiguration in types.py
    status: pending
  - id: agent-core
    content: Update construct_UIBlockConfiguration to copy type_metadata to data_type_metadata
    status: pending
  - id: agent-tests
    content: Add tests for type_metadata passing in agent_test.py
    status: pending
  - id: docs
    content: Document type_metadata field in input_data/index.md
    status: pending
  - id: mcp-agent
    content: Add data_type_metadata argument to generate_ui_component MCP tool
    status: pending
  - id: mcp-readme
    content: Update MCP tool descriptions in README.md
    status: pending
  - id: mcp-tests
    content: Add MCP tests for data_type_metadata passing
    status: pending
  - id: a2a-agent
    content: Update _data_selection to extract and pass type_metadata
    status: pending
  - id: a2a-readme
    content: Update A2A README with type_metadata documentation
    status: pending
  - id: a2a-tests
    content: Add A2A tests for type_metadata passing
    status: pending
isProject: false
---

# Add InputData.type_metadata Field Feature

## Overview

This feature adds an optional `type_metadata` string field to `InputData` that flows through to `UIBlockConfiguration` as `data_type_metadata`. The primary use case is passing tool call arguments used to load data, enabling the frontend to refresh data using the same parameters.

## Core Type Changes

### 1. Update `[libs/next_gen_ui_agent/types.py](libs/next_gen_ui_agent/types.py)`

**InputData TypedDict (line ~268):**

- Add new optional field: `type_metadata: NotRequired[str | None]`
- Description: "Optional type specific metadata, passed to the renderer. For example Tool call arguments used to load these data can be passed this way."

**UIBlockConfiguration Pydantic model (line ~399):**

- Add new optional field: `data_type_metadata: Optional[str]`
- Description: "Optional type specific metadata from InputData, passed to the renderer. For example Tool call arguments used to load the data can be used by frontend to refresh data."
- Place after `data_type` field for logical grouping

## Agent Core Logic

### 2. Update `[libs/next_gen_ui_agent/agent.py](libs/next_gen_ui_agent/agent.py)`

**In `construct_UIBlockConfiguration` method (line ~206):**

- Extract `type_metadata` from `input_data` using `input_data.get("type_metadata")`
- Pass it to `UIBlockConfiguration` constructor as `data_type_metadata` parameter
- Location: Around line 240 where `UIBlockConfiguration` is created

## Agent Core Tests

### 3. Update `[libs/next_gen_ui_agent/agent_test.py](libs/next_gen_ui_agent/agent_test.py)`

**Add new test in `TestConstructUIBlockConfiguration` class (after line ~887):**

- Test name: `test_construct_UIBlockConfiguration_with_type_metadata`
- Create `InputData` with `type_metadata='{"arg1": "value1"}'`
- Create `UIComponentMetadata` with standard fields
- Call `agent.construct_UIBlockConfiguration()`
- Assert `configuration.data_type_metadata == '{"arg1": "value1"}'`

**Update existing test (line ~620):**

- `test_construct_UIBlockConfiguration_all_info`: Add `type_metadata` to input and assert it's preserved
- Add assertion: `assert configuration.data_type_metadata == <expected_value>`

## Documentation

### 4. Update `[docs/guide/input_data/index.md](docs/guide/input_data/index.md)`

**In "InputData object fields" section (after line ~22):**

- Add new bullet point after `type` field description
- Content: `* type_metadata` - optional string with type specific metadata passed to the renderer. Example: JSON-serialized tool call arguments used to load the data, enabling frontend to refresh data with same parameters.

## MCP Protocol Integration

### 5. Update `[libs/next_gen_ui_mcp/agent.py](libs/next_gen_ui_mcp/agent.py)`

**In `generate_ui_component` tool (line ~270):**

- Add new parameter after `data_type` (around line ~302):
  - Name: `data_type_metadata`
  - Type: `Annotated[str | None, Field(...)]`
  - Default: `None`
  - Description via `_get_argument_description()`: "Arguments of tool call used for 'data' argument. COPY of tool arguments. Do not change anything! NEVER generate this."
- Pass `type_metadata=data_type_metadata` when creating `InputData` object (line ~329)

**In `generate_ui_multiple_components` tool (line ~372):**

- Update `structured_data` argument description to mention the new `type_metadata` field
- The field should already work since `InputData` TypedDict is used directly

### 6. Update `[libs/next_gen_ui_mcp/README.md](libs/next_gen_ui_mcp/README.md)`

**In `generate_ui_component` section (line ~330):**

- Add new parameter documentation after `data_type` (around line ~341):
  - `data_type_metadata` (str, optional): Arguments of tool call used for 'data' argument

**In `generate_ui_multiple_components` section (line ~231):**

- Update `structured_data` description (line ~243) to mention: "Each object has to have `id`, `data`, `type`, and optionally `type_metadata` field."

## MCP Tests

### 7. Update `[libs/next_gen_ui_mcp/agent_test.py](libs/next_gen_ui_mcp/agent_test.py)`

**Add test in `TestGenerateUIComponent` class:**

- Test name: `test_data_type_metadata_passed_through`
- Call `generate_ui_component` with `data_type_metadata='{"tool": "search", "query": "test"}'`
- Assert `output.blocks[0].configuration.data_type_metadata == '{"tool": "search", "query": "test"}'`

**Update existing test (around line ~273):**

- `test_data_configuration`: Add `data_type_metadata` to tool call and verify in assertion

**Add test in `TestGenerateUIMultipleComponents` class:**

- Test name: `test_structured_data_with_type_metadata`
- Create `input_data` with `type_metadata` field
- Call tool and verify it's preserved in output configuration

## A2A Protocol Integration

### 8. Update `[libs/next_gen_ui_a2a/agent_executor.py](libs/next_gen_ui_a2a/agent_executor.py)`

**In `_data_selection` method (line ~18):**

- Extract `type_metadata` from metadata the same way `type` is extracted
- Around line ~40-42: Add check for `metadata.get("type_metadata")` and store in `type_metadata` variable
- Pass `type_metadata=type_metadata` when creating `InputData` (line ~44-49)
- For DataPart metadata (line ~54-55): Extract `type_metadata` similarly
- Pass to `InputData` creation at line ~57-59

### 9. Update `[libs/next_gen_ui_a2a/README.md](libs/next_gen_ui_a2a/README.md)`

**In "Input" section (line ~176):**

- Update description (around line ~180) to mention `type_metadata` metadata item can be provided alongside `data` and `type`

## A2A Tests

### 10. Update `[libs/next_gen_ui_a2a/agent_executor_test.py](libs/next_gen_ui_a2a/agent_executor_test.py)`

**Add new test:**

- Test name: `test_agent_executor_with_type_metadata`
- Create message with TextPart containing metadata with `data`, `type`, and `type_metadata`
- Execute and verify `ui_block.configuration.data_type_metadata` matches input

**Update existing test (line ~55):**

- `test_agent_executor_one_part_input_with_metadata`: Add `type_metadata` to metadata and assert it appears in output

## Implementation Notes

- The field is optional everywhere, so backward compatibility is maintained
- No database migrations needed (all in-memory data structures)
- The value is passed through unchanged - no transformation or validation
- Example usage: `{"tool": "search_movies", "args": {"title": "Toy Story"}}`
- Frontend can deserialize this JSON to make refresh calls with same parameters


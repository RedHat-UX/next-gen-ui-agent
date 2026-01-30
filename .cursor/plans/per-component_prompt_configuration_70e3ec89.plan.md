---
name: Per-component prompt configuration
overview: Add per-component prompt configuration within data_types, enable HBC mixing with dynamic components, add validation for multi-HBC descriptions, and update documentation.
todos:
  - id: schema-update
    content: Add prompt field to AgentConfigComponent in types.py with proper Field() for JSON schema generation
    status: completed
  - id: validation
    content: "Update validation in component_selection_pertype.py: remove HBC mixing restriction, add multi-HBC description validation"
    status: completed
  - id: metadata-merge
    content: Create merge_per_component_prompt_overrides() function in component_metadata.py
    status: completed
  - id: prompt-construction
    content: Store full config in strategies, add data_type parameter to select_component(), handle llm_configure merging internally, update caching
    status: completed
  - id: integration
    content: Delete select_component_with_llm_async() function, unify agent.py branching into single strategy call with data_type
    status: completed
  - id: tests
    content: Create comprehensive unit tests for validation and prompt merging
    status: completed
  - id: docs-main
    content: Update docs/guide/data_ui_blocks/index.md with detailed selection and prompt explanation
    status: completed
  - id: docs-config
    content: Update docs/guide/configuration.md with configuration reference and examples
    status: completed
isProject: false
---

# Per-Component Prompt Configuration

## Overview

Enable per-component prompt customization within `data_types.components[]` configuration, allowing each component option to have its own prompt overrides. Additionally, lift the restriction preventing HBCs from being mixed with dynamic components, and validate that HBCs have descriptions when multiple components are configured.

## Architecture Changes

### 1. Configuration Schema Updates

**File: `[libs/next_gen_ui_agent/types.py](libs/next_gen_ui_agent/types.py)**`

Add a `prompt` field to `AgentConfigComponent` (line 68) with proper Field() for JSON schema generation:

```python
class AgentConfigComponent(BaseModel):
    component: str = Field(...)  # existing
    configuration: Optional[AgentConfigDynamicComponentConfiguration] = Field(...)  # existing
    llm_configure: Optional[bool] = Field(...)  # existing
    
    prompt: Optional[AgentConfigPromptComponent] = Field(
        default=None,
        description="Optional prompt customization for this component. Overrides global prompt.components configuration for this component in this data_type context. Has the same fields as AgentConfigPromptComponent. For HBCs in multi-component scenarios, at least 'description' field is required.",
    )
    """Optional prompt customization for this component."""
```

**Important**: Use Pydantic's `Field()` with `description` parameter to ensure proper JSON schema generation for config validation and IDE support.

This allows configuration like:

```yaml
data_types:
  movie-list:
    components:
   - component: table
        prompt:
          description: "Custom table description for movies"
   - component: set-of-cards
        prompt:
          description: "Custom cards description"
```

### 2. Validation Logic

**File: `[libs/next_gen_ui_agent/component_selection_pertype.py](libs/next_gen_ui_agent/component_selection_pertype.py)**`

In `init_pertype_components_mapping()` function (around line 35-92):

- **Remove HBC mixing restriction** (lines 83-91): Delete the validation that prevents HBCs from being mixed with dynamic components
- **Add multi-HBC validation**: When multiple components are configured for a data_type, check if any are HBCs. For each HBC, validate that `component.prompt.description` is defined
- Keep existing validations for `llm_configure` and `configuration` fields

Example validation logic:

```python
# Count HBCs in the list
hbc_components = [c for c in components if c.component not in DYNAMIC_COMPONENT_NAMES]

# If multiple components with HBCs, validate descriptions
if len(data_type_config.components) > 1 and hbc_components:
    for hbc in hbc_components:
        if not (hbc.prompt and hbc.prompt.description):
            raise ValueError(
                f"HBC '{hbc.component}' for data type '{data_type}' must have "
                f"prompt.description defined when multiple components are configured"
            )
```

**Note**: `chart_*` and `twostep_step2_*` fields are not used for HBC prompts - document but don't validate (validation would be complex and unnecessary).

### 3. Prompt Construction and Caching

**File: `[libs/next_gen_ui_agent/component_selection_pertype.py](libs/next_gen_ui_agent/component_selection_pertype.py)**`

**Major simplification**: Delete `select_component_with_llm_async()` function entirely!

- Move the `llm_configure=False` merging logic (currently lines 261-278) into the strategy classes
- Strategy now handles this internally in `select_component()` method after `perform_inference()` returns
- **Delete `select_component_with_llm_async()` function** - no longer needed!

**File: `[libs/next_gen_ui_agent/component_selection_llm_onestep.py](libs/next_gen_ui_agent/component_selection_llm_onestep.py)**` and `**[component_selection_llm_twostep.py](libs/next_gen_ui_agent/component_selection_llm_twostep.py)**`

- **Store full config**: In `__init__`, store `self.config = config` (currently only stores `selectable_components`)
- Add optional `data_type` parameter to `select_component()` method (public API)
- Pass `data_type` down to `perform_inference()`
- **Remove BOTH `allowed_components` and `components_config` parameters** - no longer needed!
- Update `_get_or_build_system_prompt()` to accept `data_type` parameter
- **Determine allowed components internally**:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - When `data_type` is provided: Extract from `self.config.data_types[data_type].components`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - When `data_type` is None: Use `self.config.selectable_components`
- **Update cache structure and key logic**:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Change cache type hint from `dict[frozenset[str], str]` to `dict[str | None, str]`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - When `data_type` is provided: Use `data_type` string as cache key (e.g., `"movies"`, `"products"`)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - When `data_type` is None (global selection): Use `None` as cache key (valid in Python dicts)
- Extract prompt overrides from components' `.prompt` field (when data_type provided)
- Build merged metadata and use it via `set_active_component_metadata()` before building prompt
- **Handle `llm_configure=False` merging internally** in `select_component()` after inference (moved from `select_component_with_llm_async`)

**Caching strategy rationale**:

- Each data_type has exactly ONE set of components configured, so data_type alone is sufficient as cache key
- Global selection (no data_type) has ONE set of selectable components, so None is sufficient
- Much simpler than including components in the key
- Memory overhead is minimal: typically 5-10 data_types + 1 global = ~11 cache entries

### 4. Metadata Merging

**File: `[libs/next_gen_ui_agent/component_metadata.py](libs/next_gen_ui_agent/component_metadata.py)**`

Create new function `merge_per_component_prompt_overrides()`:

```python
def merge_per_component_prompt_overrides(
    base_metadata: dict[str, dict[str, Any]],
    components_list: list[AgentConfigComponent]
) -> dict[str, dict[str, Any]]:
    """Merge per-component prompt overrides into metadata.
    
    Args:
        base_metadata: Base metadata (already includes global overrides)
        components_list: List of components with potential prompt overrides
        
    Returns:
        Metadata with per-component overrides applied
    """
```

This function:

1. Takes base metadata (already has global `config.prompt.components` applied)
2. Iterates through `components_list`
3. For each component with `.prompt` defined, merges those overrides
4. Returns final merged metadata

### 5. Component Selection Flow (Unified!)

**In `agent.py` `select_component()` method:**

```python
# Try single-component or HBC selection first (no LLM needed)
component = select_component_per_type(input_data, json_data)
if component:
    # ... set metadata and return

# LLM-based selection (unified for both data_type-specific and global)
data_type = input_data.get("type")  
component = await self._component_selection_strategy.select_component(
    inference, 
    user_prompt, 
    input_data_for_strategy,
    data_type=data_type,  # Pass data_type (or None for global)
)
```

**In strategy `select_component()` method:**

1. Determine allowed components based on `data_type`:
  - If `data_type`: Look up `self.config.data_types[data_type].components`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - If `None`: Use `self.config.selectable_components`
2. Extract prompt overrides from components' `.prompt` field (if data_type)
3. Merge metadata:
  - Base `COMPONENT_METADATA`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Global `self.config.prompt.components` overrides
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Per-component `component.prompt` overrides (if data_type)
4. Call `perform_inference()` with `data_type` for caching
5. Build system prompt using merged metadata and cache it with `data_type` as key
6. If result has no fields and `llm_configure=False`, merge with pre-configuration
7. Return complete `UIComponentMetadata`

**Simplification benefits:**

- `**select_component_with_llm_async()` function deleted** - no longer needed!
- **No branching in agent.py** - single unified path for LLM selection
- **Strategy interface is simpler**: just `data_type` parameter (net change: -2 parameters, +1 parameter)
- All data_type and component filtering logic centralized in strategy
- Cleaner, more maintainable code

## Testing Strategy

Create comprehensive unit tests in new file: `libs/next_gen_ui_agent/component_selection_pertype_test.py`

**Test cases:**

1. **Validation tests** (`test_init_pertype_validation_*`):
  - Multi-component with HBC without description → ValueError
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Multi-component with HBC with description → Success
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Single HBC without description → Success (no validation needed)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Multiple HBCs with descriptions → Success
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - HBC mixed with dynamic components → Success (restriction lifted)
2. **Prompt override tests** (`test_per_component_prompt_*`):
  - Per-component prompt overrides are applied correctly
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Per-component overrides take precedence over global
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Multiple components with different prompts
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Chart and twostep fields in HBC component prompt (should work, not validated)
3. **Caching tests** (`test_system_prompt_caching_*`):

**Test: `test_cache_hit_for_same_data_type**`

```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Create strategy with data_type "movies" configured
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Call `_get_or_build_system_prompt("movies")` twice
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert `_build_system_prompt()` was called only once (using spy/mock)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert both calls return the exact same string object (using `is` not `==`)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert cache dict has exactly one entry with key `"movies"`
```

**Test: `test_different_cache_entries_per_data_type**`

```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Configure two data_types: "movies" and "products" with different prompt overrides
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Call `_get_or_build_system_prompt("movies")`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Call `_get_or_build_system_prompt("products")`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert cache has 2 entries: keys `"movies"` and `"products"`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert the two cached prompts are different strings
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Verify prompts contain the respective custom descriptions
```

**Test: `test_global_selection_uses_none_key**`

```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Call `_get_or_build_system_prompt(None)` twice (no data_type)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert cache has entry with key `None`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert second call returns cached prompt (same object)
```

**Test: `test_cache_isolation_data_type_vs_global**`

```
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Configure data_type "movies" with custom prompt
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Call with data_type: `_get_or_build_system_prompt("movies")`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Call without data_type: `_get_or_build_system_prompt(None)`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert cache has 2 entries: `"movies"` and `None`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Assert prompts are different (global doesn't have custom overrides)
```

1. **Integration tests** (update existing tests):
  - Update `libs/next_gen_ui_agent/component_metadata_test.py` for new merge function
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Update strategy tests to handle custom metadata and data_type parameters
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            - Test unified agent.py flow with and without data_type

## Documentation Updates

### `[docs/guide/data_ui_blocks/index.md](docs/guide/data_ui_blocks/index.md)`

**Section to update: "Selection and Configuration process" (lines 11-39)**

Add detailed explanation:

- How per-component prompt configuration works
- Precedence: base → global prompt overrides → per-component overrides
- Example showing HBC with description in multi-component config
- Note that HBCs can now be mixed with dynamic components
- Explain prompt construction flow with diagram

**New subsection: "Prompt Customization for Component Selection"**

Explain:

- When prompts are used (multi-component selection scenarios)
- Which fields are relevant for different component types
- For HBCs: Only `description` field is used for component selection
- `chart_*` and `twostep_step2_*` fields are not used for HBCs but accepted in config (no validation)
- Precedence of overrides with examples

### `[docs/guide/configuration.md](docs/guide/configuration.md)`

**Section: `components` field (line 69-81)**

Update to mention:

- Each component can have `prompt` field
- Link to detailed description in data_ui_blocks/index.md
- Brief example showing prompt field

**New subsection under `components`: `prompt` [`AgentConfigPromptComponent`, optional]**

```markdown
##### `prompt` [`AgentConfigPromptComponent`, optional]

Customize LLM prompts for this specific component when it's used in multi-component selection.
Has the same fields as global `[prompt.components](#components-dictstr-agentconfigpromptcomponent-optional)`.
Overrides global prompt configuration for this component in this data_type context.

For detailed explanation of how prompt construction works, see [Data UI Blocks selection process](data_ui_blocks/index.md#selection-and-configuration-process).

**Note**: Hand-build components (HBCs) must have at least `description` defined when multiple components 
are configured for a data_type. Chart-specific fields (`chart_*`) and two-step strategy fields 
(`twostep_step2_*`) are not used for HBCs but are accepted in configuration (not validated).
```

**Update note about HBC mixing** (line 80):

Change from:

> **Note**: Hand Build Components cannot be mixed with other components now.

To:

> **Note**: When using Hand Build Components in multi-component configuration, each HBC must have `prompt.description` defined for LLM selection.

### Configuration Examples

Add to `[docs/guide/configuration.md](docs/guide/configuration.md)` after line 296:

```yaml
# Per-component prompt customization
data_types:
  product-data:
    components:
      # Dynamic component with custom prompt
   - component: table
        prompt:
          description: "Use table for structured product listings with many items"
          twostep_step2_rules: "Always include product ID and price"
      
      # HBC with required description (multi-component scenario)
   - component: products:detail-view
        prompt:
          description: "Use custom product detail view for single product with images"
      
      # Chart with custom prompt
   - component: chart-bar
        llm_configure: true
        prompt:
          description: "Use bar chart for product category comparisons"
          chart_description: "Product sales by category"
          # Note: chart_* and twostep_step2_* fields accepted but not used for HBCs
```

## Files Modified Summary

**Core Logic:**

- `libs/next_gen_ui_agent/types.py` - Add `prompt` field to `AgentConfigComponent`
- `libs/next_gen_ui_agent/component_selection_pertype.py` - Validation, HBC mixing, **delete `select_component_with_llm_async()**`
- `libs/next_gen_ui_agent/component_metadata.py` - New merge function for per-component overrides
- `libs/next_gen_ui_agent/component_selection_llm_onestep.py` - Add data_type param, store full config, handle merging
- `libs/next_gen_ui_agent/component_selection_llm_twostep.py` - Add data_type param, store full config, handle merging
- `libs/next_gen_ui_agent/agent.py` - **Unify branching**, single call to strategy with data_type

**Tests:**

- `libs/next_gen_ui_agent/component_selection_pertype_test.py` - NEW: Comprehensive tests
- `libs/next_gen_ui_agent/component_metadata_test.py` - Update for new merge function

**Documentation:**

- `docs/guide/data_ui_blocks/index.md` - Main detailed description
- `docs/guide/configuration.md` - Configuration reference

## Implementation Notes

- Maintain backward compatibility: `prompt` field is optional
- Per-component prompts only matter for multi-component data_type configs
- Single-component configs bypass LLM, so prompts are unused
- For HBCs: Only `description` field is meaningful; `chart_*` and `twostep_step2_*` fields are accepted but not used (no validation for config flexibility)
- Validation only at startup in `init_pertype_components_mapping()`

**JSON Schema generation**:

- New `prompt` field MUST use Pydantic `Field()` with `description` parameter
- This ensures proper JSON schema generation for config validation
- Enables IDE autocomplete and validation when editing YAML configs

**Caching considerations**:

- Cache key is simply `data_type` string (e.g., `"movies"`) for data_type-specific selections
- Cache key is `None` for global selections
- Each data_type has exactly one component set configured, so no need to include components in key
- Memory overhead is minimal: typically 5-10 data_types + 1 global = ~11 cache entries × 2-5KB = ~55KB total


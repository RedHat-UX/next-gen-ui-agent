# Chart Component Integration Summary

This document summarizes the integration of the ChartComponent into the Next Gen UI Agent.

## What Was Done

The ChartComponent from `@rhngui/patternfly-react-renderer` has been fully integrated into the agent system. Here's what was added:

### 1. Component Schema (`spec/component/chart.schema.json`)
- Defined JSON schema for the chart component specification
- Supports bar, line, pie, and donut chart types
- Defines data structure with series and data points

### 2. Python Types (`libs/next_gen_ui_agent/data_transform/types.py`)
- Added `ChartDataPoint` class for individual data points
- Added `ChartSeries` class for data series
- Added `ComponentDataChart` class for complete chart configuration

### 3. Data Transformer (`libs/next_gen_ui_agent/data_transform/chart.py`)
- Created `ChartDataTransformer` to transform input data into chart format
- Handles multiple input data formats:
  - Pre-structured chart data with series
  - Flat key-value data (converted to single series)
  - Array of objects (converted to data points)
- Includes validation for required fields

### 4. Component Registration
- **`libs/next_gen_ui_agent/data_transformation.py`**: Added ChartDataTransformer to COMPONENT_TRANSFORMERS_REGISTRY
- **`libs/next_gen_ui_agent/component_selection_pertype.py`**: Added chart to DYNAMIC_COMPONENT_NAMES
- **React Renderer**: ChartComponent already registered in `componentsMap` at `/Users/jschuler/Code/next-gen-ui-react/src/constants/componentsMap.ts`

### 5. LLM Integration
Updated component descriptions in both LLM selection strategies:
- **`component_selection_llm_onestep.py`**: Added chart to ui_components_description_supported
- **`component_selection_llm_twostep.py`**: Added chart to ui_components_description_supported

The LLM now knows to use charts for "numeric data that needs to be compared or visualized graphically"

### 6. Tests (`libs/next_gen_ui_agent/data_transform/chart_test.py`)
Created comprehensive test suite covering:
- Processing pre-structured chart data with series
- Processing flat key-value data
- Processing array of objects
- Processing data with x/y fields
- Validation of required fields

### 7. Documentation (`spec/component/README.md`)
Added Chart component documentation with example JSON output

## How to Use

### Option 1: Configure by Data Type

Add chart configuration to your agent config YAML:

```yaml
component_system: json
data_types:
  sales:data:
    components:
      - component: chart
        configuration:
          title: "Sales Chart"
          chartType: "bar"
```

### Option 2: Let the LLM Decide

The agent's LLM will automatically select the chart component when it detects numeric data that should be visualized:

```python
from next_gen_ui_agent import NextGenUIAgent, AgentInput, InputData

agent = NextGenUIAgent(config=agent_config, inference=your_llm)

input_data = InputData(
    id="sales_data",
    data={
        "data": [
            {
                "name": "Q1",
                "data": [
                    {"x": "Jan", "y": 100},
                    {"x": "Feb", "y": 150},
                    {"x": "Mar", "y": 200}
                ]
            }
        ],
        "chartType": "bar"
    }
)

result = await agent.component_selection(
    AgentInput(
        user_prompt="Show me the sales data as a chart",
        input_data=[input_data]
    )
)
```

### Option 3: Explicitly Request Hand-Build Component

```python
input_data = InputData(
    id="chart_1",
    hand_build_component_type="chart",
    data={
        "data": [...],  # your chart data
        "chartType": "line"
    }
)
```

## Supported Chart Types

- **bar**: Vertical bar chart for comparing values across categories
- **line**: Line chart for showing trends over time
- **pie**: Pie chart for showing proportions
- **donut**: Donut chart similar to pie with center area

## Data Format

The transformer accepts multiple input formats and converts them to the standard chart format:

### Standard Format (Recommended)
```json
{
  "data": [
    {
      "name": "Series 1",
      "data": [
        {"x": "Category A", "y": 100},
        {"x": "Category B", "y": 150}
      ]
    }
  ],
  "chartType": "bar"
}
```

### Flat Key-Value
```json
{
  "Apples": 45,
  "Oranges": 30,
  "Bananas": 25,
  "chartType": "pie"
}
```

### Array of Objects
```json
[
  {"name": "Jan", "value": 100},
  {"name": "Feb", "value": 150}
]
```

## Next Steps

1. **Test the integration**: Run your agent with chart data to verify it works
2. **Customize**: Adjust the LLM prompts if needed for your specific use cases
3. **Add examples**: Create example notebooks or scripts demonstrating chart usage
4. **Extend**: Add more chart types or customization options as needed

## Notes

- The linked `@rhngui/patternfly-react-renderer` package already has the ChartComponent implemented
- Changes are automatically available since the package is npm-linked
- No version bump needed during development with npm link
- All Python tests follow the existing pattern and should pass with the build system

## Troubleshooting

### Pants Build System with npm link

If you encounter errors like:
```
IntrinsicError: While expanding link "tests/ngui-e2e/client/node_modules/@rhngui/patternfly-react-renderer": 
Globs may not traverse outside of the buildroot
```

This happens because Pants tries to traverse the npm link symlink. The fix is already applied in `pants.toml`:

```toml
pants_ignore = [
  "requirements_dev.txt",
  "**/node_modules/**",
  "tests/ngui-e2e/client/node_modules",
  "tests/ngui-e2e-edit/client/node_modules"
]
```

This tells Pants to ignore `node_modules` directories entirely, preventing symlink traversal issues.


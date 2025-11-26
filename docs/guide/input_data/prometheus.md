# Prometheus Input Data Transformer

The Prometheus Input Data Transformer enables the NGUI agent to process time-series metrics from Prometheus and automatically generate chart visualizations.

## Overview

This transformer converts Prometheus `query_range` results (with `resultType="matrix"`) into a normalized format that the NGUI agent's chart component can process.

## Installation

The Prometheus transformer is built-in and available automatically when you use the NGUI agent. No additional installation is required.

## Input Format

The transformer expects Prometheus `/api/v1/query_range` response format:

```json
{
  "result": [
    {
      "metric": {
        "__name__": "instance:node_cpu_utilisation:rate1m",
        "pod": "node-exporter-zv64p",
        "instance": "ip-10-0-18-210.ec2.internal"
      },
      "values": [
        [1763032771.933, "0.051437499999995695"],
        [1763032831.933, "0.0499583333333351"]
      ]
    }
  ],
  "resultType": "matrix"
}
```

## Output Format

The transformer produces a normalized structure:

```json
{
  "metadata": {
    "source": "prometheus",
    "resultType": "matrix"
  },
  "series": [
    {
      "name": "node-exporter-zv64p",
      "metric": {
        "__name__": "instance:node_cpu_utilisation:rate1m",
        "pod": "node-exporter-zv64p",
        "instance": "ip-10-0-18-210.ec2.internal"
      },
      "dataPoints": [
        {
          "timestamp": 1763032771.933,
          "value": 0.0514,
          "time": "14:32"
        },
        {
          "timestamp": 1763032831.933,
          "value": 0.0500,
          "time": "14:33"
        }
      ]
    }
  ]
}
```

## Configuration

### Agent Configuration File

```yaml
data_types:
  prometheus_metrics:
    data_transformer: prometheus
    components:
      - component: chart
        configuration:
          fields:
            - name: "Time"
              data_path: "series[*].dataPoints[*].time"
            - name: "Value"
              data_path: "series[*].dataPoints[*].value"
```

### Python Code

```python
from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.types import InputData
import json

# Initialize agent with configuration
agent = NextGenUIAgent.from_config_file("config.yaml")

# Prepare Prometheus data
prometheus_data = {
    "result": [{
        "metric": {"pod": "my-pod"},
        "values": [[1700000000, "0.5"], [1700000060, "0.6"]]
    }],
    "resultType": "matrix"
}

input_data = InputData(
    id="cpu-metrics",
    type="prometheus_metrics",  # Maps to config
    data=json.dumps(prometheus_data)
)

# Generate UI component
result = await agent.select_component(
    user_prompt="Show CPU utilization over time",
    input_data=input_data
)
```

## Series Name Extraction

The transformer automatically extracts meaningful series names from Prometheus metric labels using this priority order:

1. `pod`
2. `instance`
3. `job`
4. `container`
5. `node`
6. `__name__`

If none of these labels exist, it uses the first available label or defaults to "Series".

## Timestamp Formatting

Timestamps are automatically converted from Unix timestamps to `HH:MM` format for display on charts. The original timestamp is preserved in the `timestamp` field for other use cases.

## Use Cases

### Time-Series Line Charts

Best for visualizing metrics over time:

```yaml
data_types:
  prometheus_metrics:
    data_transformer: prometheus
    components:
      - component: chart
        configuration:
          fields:
            - name: "Time"
              data_path: "series[*].dataPoints[*].time"
            - name: "CPU Usage"
              data_path: "series[*].dataPoints[*].value"
```

User query: "Show me CPU usage over the last hour"

### Aggregated Pie/Donut Charts

For showing current distribution across multiple series:

```yaml
data_types:
  prometheus_aggregated:
    data_transformer: prometheus
    components:
      - component: chart
        configuration:
          fields:
            - name: "Pod"
              data_path: "series[*].name"
            - name: "Memory Usage"
              data_path: "series[*].dataPoints[-1].value"
```

User query: "Show memory usage by pod as a pie chart"

### Multiple Series Comparison

For comparing multiple time-series on the same chart:

The transformer automatically handles multiple series in the result. Each series becomes a separate line/bar in the chart.

## Integration with MCP Servers

### Example: Genie Plugin Architecture

```python
# In your MCP server that queries Prometheus
@mcp_server.tool()
async def get_prometheus_metrics(query: str, duration: str) -> str:
    # Query Prometheus
    result = await prometheus_client.query_range(
        query=query,
        start=time.time() - parse_duration(duration),
        end=time.time(),
        step='1m'
    )
    
    # Return raw Prometheus format
    # NGUI agent will transform it automatically
    return json.dumps(result)

# In your LLM/OLS orchestration
async def handle_metrics_query(user_query: str):
    # Step 1: LLM queries Prometheus via MCP tool
    prom_data = await get_prometheus_metrics(
        query="instance:node_cpu_utilisation:rate1m",
        duration="1h"
    )
    
    # Step 2: Pass to NGUI agent with type hint
    ui_config = await ngui_agent.select_component(
        user_prompt=user_query,
        input_data=InputData(
            id="cpu-metrics",
            type="prometheus_metrics",  # Uses Prometheus transformer
            data=prom_data
        )
    )
    
    # Step 3: Return chart configuration
    return ui_config
```

## Error Handling

The transformer includes robust error handling:

- **Invalid JSON**: Raises `ValueError` with clear message
- **Missing fields**: Raises `ValueError` explaining required structure
- **Non-matrix types**: Logs warning but attempts to process
- **Invalid values**: Skips individual invalid data points, continues processing
- **Empty series**: Filters out series with no data points

## Testing

### Unit Tests

Run the test suite:

```bash
# Using pants
./pants test libs/next_gen_ui_agent/input_data_transform:tests

# Or specific test file
./pants test libs/next_gen_ui_agent/input_data_transform/prometheus_input_data_transformer_test.py
```

### Interactive End-to-End Testing

The NGUI test UI includes a **Prometheus Converter** tab that allows you to test the full production pipeline:

1. Start the test server:
   ```bash
   cd tests/ngui-e2e/server
   ./start_server.sh
   ```

2. Start the frontend:
   ```bash
   cd tests/ngui-e2e/client
   npm install
   npm run dev
   ```

3. Open the test UI and navigate to the **📊 Prometheus** tab in the test panel

4. Paste your Prometheus `query_range` result JSON and click **Convert & Send**

This will:
- Send your Prometheus data to the `/test-prometheus` backend endpoint
- Invoke the `PrometheusInputDataTransformer` to normalize the data
- Pass the normalized data to the NGUI agent with the LLM
- The LLM will select an appropriate chart component and configuration
- Return the chart configuration to display in the UI

This provides a realistic test of the entire workflow, including:
- Data transformation (Prometheus → normalized format)
- Component selection (LLM choosing chart type)
- Field mapping (LLM extracting data paths)
- Chart rendering (PatternFly React Charts)

## Advanced Usage

### Custom Timestamp Formatting

To customize timestamp formatting, you can extend the transformer:

```python
from next_gen_ui_agent.input_data_transform.prometheus_input_data_transformer import (
    PrometheusInputDataTransformer
)
from datetime import datetime

class CustomPrometheusTransformer(PrometheusInputDataTransformer):
    def _format_timestamp(self, timestamp: float) -> str:
        """Custom format: MM/DD HH:MM"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%m/%d %H:%M")
```

### Using Different Metric Labels

To change the priority order for series name extraction:

```python
class CustomPrometheusTransformer(PrometheusInputDataTransformer):
    METRIC_LABEL_PRIORITY = ["custom_label", "pod", "instance"]
```

## References

- [NGUI Agent Documentation](/)
- [Prometheus Query API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [Genie Plugin Example](https://github.com/jhadvig/genie-plugin)
- [Input Data Transformers Source Code](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/input_data_transform)
- [Chart Component Source Code](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/libs/next_gen_ui_agent/data_transform/chart.py)


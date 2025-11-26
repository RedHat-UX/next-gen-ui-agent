# Testing Prometheus Data with NGUI Agent

This guide explains how to test Prometheus time-series data with the NGUI agent using the production backend transformer.

## Quick Start

### Test with Real Backend Transformer

1. Go to the **📊 Prometheus** tab in the Test Panel
2. Click **Load Example** or paste your Prometheus API response JSON
3. Configure chart settings:
   - **Title**: Chart title
   - **Chart Type**: Line or Bar
   - **Downsample**: Take every Nth data point (useful for large datasets)
4. Click **Convert & Send to Chat**

This method tests the **full production pipeline**:
- Sends data to `/test-prometheus` backend endpoint
- Uses the real `PrometheusInputDataTransformer`
- Invokes the NGUI agent to generate the chart configuration
- Returns the same output you'd get in production

## Prometheus Data Format

The backend transformer expects the standard Prometheus range query result format:

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

**Key Points:**
- `result` is an array of time series
- Each series has a `metric` object (labels) and `values` array
- `values` is an array of `[timestamp, value]` pairs
- Timestamps are Unix timestamps in seconds
- Values are strings that will be converted to numbers

## Getting Prometheus Data

### From Prometheus API

```bash
curl --request POST \
  --url http://localhost:8080/v1/streaming_query \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "gpt-4-turbo",
    "provider": "openai",
    "query": "what was the cpu usage over the last hour?"
  }'
```

The response will include a `tool_execution` event with the Prometheus data in the `response` field.

### From Prometheus Directly

```bash
curl 'http://prometheus-server:9090/api/v1/query_range' \
  --data-urlencode 'query=instance:node_cpu_utilisation:rate1m' \
  --data-urlencode 'start=2025-01-15T12:00:00Z' \
  --data-urlencode 'end=2025-01-15T13:00:00Z' \
  --data-urlencode 'step=1m'
```

Extract the `data` field from the response and paste it into the converter.

## Backend Transformer

The Prometheus tab uses the production `PrometheusInputDataTransformer` located at:
```
libs/next_gen_ui_agent/input_data_transform/prometheus_input_data_transformer.py
```

This ensures your testing matches exactly what happens in production. The transformer:
- Converts Prometheus `matrix` format to normalized time-series
- Extracts series names from metric labels (priority: pod → instance → job → container → __name__)
- Formats timestamps as HH:MM (e.g., "06:19")
- Can handle multiple series in a single result

For detailed documentation on the transformer, see: [Prometheus Input Data Transformer Guide](../../docs/guide/input_data/prometheus.md)

## Supported Chart Types

- **Line** - Best for time-series data (default)
- **Bar** - Alternative visualization for time-series or categorical data

## Tips

1. **Large Datasets**: Use the downsample option to reduce the number of points
   - For 1-hour data at 1-minute intervals (60 points), downsample=1 is fine
   - For 24-hour data at 1-minute intervals (1440 points), try downsample=5 or 10

2. **Multiple Series**: The backend transformer automatically handles multiple time series in the Prometheus result

3. **Metric Labels**: The backend transformer intelligently chooses series names from metric labels in this priority:
   - pod
   - instance
   - job
   - container
   - __name__

4. **Testing Different Visualizations**: 
   - Try different chart types to see what works best
   - Line charts work best for continuous time-series
   - Bar charts can work for discrete time periods

## Example Workflows

### Workflow 1: Test Your Own Prometheus Data with Backend
```
1. Get Prometheus data from your API/Prometheus server
2. Prometheus tab → Paste JSON (or Load Example)
3. Configure settings (title, chart type, downsample)
4. Convert & Send → Tests full backend pipeline
5. View rendered chart with debug info showing transformer details
6. Iterate on settings if needed
```

### Workflow 2: Test with LLM Agent
```
1. Disable Mock Mode
2. Ask: "Show me a chart of CPU utilization over the last hour"
3. Your LLM should query Prometheus and return the data
4. NGUI agent converts it to a chart automatically
```

## Troubleshooting

**"Backend error: Prometheus test error"**
- Check the terminal logs for detailed error messages
- Ensure your JSON structure matches the expected Prometheus format
- Try the "Load Example" button to see a valid format

**"Please paste Prometheus data"**
- Click "Load Example" to populate the textarea with sample data
- Or paste your own Prometheus JSON response

**Chart renders but looks wrong**
- Check Debug Information panel to see the transformer output
- Verify the backend transformer found the right metric labels
- Look at the field mappings in the debug data

**Too many data points making the chart slow**
- Increase the downsample value (try 2, 5, or 10)
- Backend will reduce points before transformation
- Check terminal logs to see: "Downsampled: X → Y points"


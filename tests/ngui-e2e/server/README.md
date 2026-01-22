# NGUI E2E Testing App API Server

[![Module Category](https://img.shields.io/badge/Module%20Category-Testing/Evaluation-darkmagenta)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)

FastAPI server with **Next Gen UI Agent** integration for AI-powered UI component generation using LlamaStack.

This testing application demonstrates the full capabilities of the Next Gen UI Agent with a RESTful API, supporting both default movie data and custom inline data with various UI component types.

## Provides

* REST API endpoints for UI component generation (`/generate`)
* Health check and LLM connectivity testing endpoints
* LlamaStack integration with SSL certificate support
* Movie search functionality with JSON-based data
* Support for inline data with custom data types
* Intelligent data filtering
* CORS-enabled for frontend integration

## Quick Start

```bash
# 1. Install dependencies
poetry install

# 2. Set environment variables
export LLAMA_STACK_BASE_URL="your-llama-stack-url"
export NGUI_MODEL="your-model-id"

# 3. Run server
poetry run uvicorn app.main:app --reload --port 8080

# 4. Test it
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me all movies in a table"}'
```

## API Endpoints

### `POST /generate`
Generate UI components from natural language.

**Request (with default movie data):**
```json
{
  "prompt": "Show me Toy Story details"
}
```

**Request (with inline data as JSON):**
```json
{
  "prompt": "Show revenue for Q1-Q4",
  "data": [
    {"quarter": "Q1", "revenue": 50000},
    {"quarter": "Q2", "revenue": 60000}
  ],
  "data_type": "revenue.quarterly",
  "skip_filtering": false
}
```

**Request (with inline data as string):**
```json
{
  "prompt": "Show me the sales report",
  "data": "{\"region\": \"US\", \"sales\": 150000, \"growth\": \"12%\"}",
  "data_type": "sales.report"
}
```

**Request Parameters:**
- `prompt` (required): Natural language description of the desired UI
- `data` (optional): Data payload - can be a JSON object, array, or JSON string. The UI Agent Core accepts string data, which is useful for passing serialized JSON or other data formats.
- `data_type` (optional): Identifier for the data type (e.g., `"movies.detail"`, `"revenue.quarterly"`)
- `skip_filtering` (optional): Skip intelligent data filtering if `true` (default: `false`). See "Intelligent Data Filtering" section below for details.

**Response:**
```json
{
  "response": {
    "component": "one-card",
    "title": "Toy Story",
    "fields": [...],
    "image": "https://..."
  },
  "metadata": {
    "model": {...},
    "component_type": "one-card",
    "data_source": {...}
  }
}
```

### `GET /api/v1/health`
Health check endpoint.

### `GET /api/v1/wdyk`
Test LLM connectivity.

## Available Movies

- Toy Story (1995)
- The Shawshank Redemption (1994)
- The Dark Knight (2008)
- Inception (2010)
- The Matrix (1999)
- Interstellar (2014)

Add more in `app/data/movies_data.json`

## Supported Components

The set of supported component types is determined by the **UI Agent Core** library and the **React renderer** ([@rhngui/patternfly-react-renderer](https://github.com/RedHat-UX/next-gen-ui-react)). No additional work is required in this application when new component types are added to those libraries.

Currently available components include:

- `one-card` - Single item with image and fields
- `set-of-cards` - Multiple card items
- `table` - Tabular data (multiple rows)
- `chart-bar` - Bar chart visualization
- `chart-line` - Line chart visualization
- `chart-pie` - Pie chart visualization
- `chart-donut` - Donut chart visualization
- `chart-mirrored-bar` - Mirrored bar chart visualization
- `video-player` - Video/trailer playback
- `image` - Image display

## Architecture

```
User Prompt → Movie Search → NGUI Agent + LLM → UI Component JSON
```

**Key Components:**
- `search_movies()` - Simple JSON-based search
- `NextGenUILlamaStackAgent` - LLM-powered component selection
- Manual `ToolStep` creation - Simulates agent tool execution

## Intelligent Data Filtering

The server includes an optional **intelligent data filtering** feature that uses the LLM to analyze user queries and filter data before passing it to the UI generation agent.

### How It Works

1. **Query Analysis**: The LLM analyzes the user's prompt to understand their intent
2. **Data Filtering**: Based on the analysis, it filters the data to return only relevant items
3. **Optimization**: Reduces the amount of data sent to the UI agent, improving performance and accuracy

### Example

**Without filtering** (skip_filtering=true):
- Query: "Show me action movies"
- Data sent to UI agent: All 6 movies in the database

**With filtering** (skip_filtering=false, default):
- Query: "Show me action movies"
- LLM analyzes query → identifies genre filter
- Data sent to UI agent: Only action movies (filtered subset)

### Implementation

Located in `data_sources/filtering.py`, the `generic_data_filter_agent()` function:
- Works with any JSON data structure (movies, cost data, RBAC permissions, etc.)
- Uses LLM to make intelligent filtering decisions
- Returns filtered data or all data if query is general
- Can be disabled per-request with `skip_filtering: true` parameter

### When to Use

- **Enable (default)**: When you want relevant data based on user intent
- **Disable**: When you need to show all data regardless of the prompt, or when working with small datasets

## Configuration

### UI Agent Configuration

Currently configured in code via `config.py`:

```python
from next_gen_ui_agent.agent_config import AgentConfig
NGUI_CONFIG = AgentConfig(unsupported_components=True)
```

**To customize:** Edit `config.py` and restart the server.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LLAMA_STACK_BASE_URL` | LlamaStack server URL (primary, works for any deployment) |
| `LIGHTRAIL_LLAMA_STACK_BASE_URL` | LlamaStack server URL (fallback, for Lightrail-specific deployments) |
| `LLAMA_STACK_TLS_CA_CERT_PATH` | SSL certificate path (primary) |
| `LIGHTRAIL_LLAMA_STACK_TLS_SERVICE_CA_CERT_PATH` | SSL certificate path (fallback, for Lightrail) |
| `NGUI_MODEL` | Model identifier (matches MCP and A2A naming convention) |

## Example Prompts

### Using Default Movie Data

```bash
# Get a card
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me about Inception"}'

# Get a table
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show all movies in a table"}'

# Get a video
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Play Toy Story trailer"}'
```

### Using Inline Data with `data` and `data_type`

```bash
# Revenue data with bar chart
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show revenue as a bar chart",
    "data": [
      {"quarter": "Q1", "revenue": 50000},
      {"quarter": "Q2", "revenue": 60000},
      {"quarter": "Q3", "revenue": 55000},
      {"quarter": "Q4", "revenue": 70000}
    ],
    "data_type": "revenue.quarterly"
  }'

# Customer orders as table
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show customer orders in a table",
    "data": [
      {"customer": "Acme Corp", "order_id": "A123", "total": 5000},
      {"customer": "Tech Inc", "order_id": "T001", "total": 8000}
    ],
    "data_type": "customer.orders"
  }'

# Product inventory as cards
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Display products as cards",
    "data": [
      {"name": "Laptop", "price": 999, "stock": 15},
      {"name": "Mouse", "price": 29, "stock": 150}
    ],
    "data_type": "products.inventory"
  }'
```

## Development

**Add movies:** Edit `app/data/movies_data.json`  
**Modify search:** Update data sources in `data_sources/` directory  
**Add data sources:** Create new modules in `data_sources/`  
**Add routes:** Create new endpoints in `routes/` directory

## Links

* [Parent E2E App README](../README.md)
* [Next Gen UI Agent Documentation](https://redhat-ux.github.io/next-gen-ui-agent/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ngui-e2e/server)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)

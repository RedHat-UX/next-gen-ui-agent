# Migration Summary: Lightrail/LlamaStack Server

This document summarizes the migration from the original LangGraph-based server to the Lightrail/LlamaStack-based server.

## What Was Migrated

### ✅ Complete Modular Structure

All code from `ngui-e2e-testing/app/` has been successfully copied to `next-gen-ui-agent/tests/ngui-e2e/server/app/`:

```
app/
├── agents/
│   ├── __init__.py
│   └── ngui.py                    # LlamaStack NGUI agent setup
├── config_legacy/                  # Legacy config (kept for reference)
│   ├── __init__.py
│   ├── prompts.py
│   └── settings.py
├── config.py                       # Main configuration (LlamaStack)
├── data/
│   └── movies_data.json           # Default movie dataset (6 movies)
├── data_sources/
│   ├── __init__.py
│   ├── default_data.py            # ✨ NEW: Default data fallback
│   ├── filtering.py               # ✨ NEW: Smart filtering agent
│   ├── inline.py                  # Inline data processing
│   └── movies.py                  # Movie data utilities
├── llm.py                         # LlamaStack client initialization
├── main.py                        # FastAPI application
├── models.py                      # Pydantic models
├── prompts.py                     # ✨ NEW: LLM prompts for filtering
├── routes/
│   ├── __init__.py
│   ├── generate.py                # Main /generate endpoint
│   └── health.py                  # Health & WDYK endpoints
└── utils/
    ├── __init__.py
    ├── agent_messages.py          # Agent message serialization
    ├── logging.py                 # Logging utilities
    ├── response.py                # Error response helpers
    └── validation.py              # NGUI response validation
```

### ✨ New Features Added

1. **Default Data Fallback** (`data_sources/default_data.py`)
   - Automatically loads `movies_data.json` when no inline data is provided
   - Graceful fallback with error handling

2. **Smart Filtering Agent** (`data_sources/filtering.py`)
   - Intelligently filters data based on user prompts
   - Detects query types: "all", "specific", "subset"
   - Uses LLM to analyze user intent

3. **Prompts Module** (`prompts.py`)
   - Centralized prompt templates for filtering agent
   - Structured JSON output format

4. **Enhanced Error Handling**
   - Standardized error codes (`ErrorCode` enum)
   - Detailed error messages with suggestions
   - HTTP status code mapping

## Key Differences from Original

### Architecture

| Aspect | Original (LangGraph) | Lightrail (LlamaStack) |
|--------|---------------------|------------------------|
| **Framework** | LangGraph | LlamaStack |
| **Agent Type** | `NextGenUIAgent` | `NextGenUILlamaStackAgent` |
| **Data Passing** | LangChain messages | `ToolExecutionStep` |
| **Config** | `AgentConfig` class | `AgentConfig` class (0.3.0+) |
| **Movies Agent** | Separate LangGraph agent | Removed (uses default data) |

### Dependencies

```toml
# Required versions (pyproject.toml)
"next-gen-ui-agent (>=0.3.0)"           # ⚠️ Must be 0.3.0+
"next-gen-ui-llama-stack (>=0.3.0)"     # ⚠️ Must be 0.3.0+
"llama-stack-client (>=0.2.15,<0.3.0)"  # Pin to 0.2.x
```

**Critical**: Version 0.2.x had a bug where data arrays were empty. Always use 0.3.0+.

### Configuration

**Environment Variables** (set by Lightrail):
```bash
LIGHTRAIL_LLAMA_STACK_BASE_URL          # LlamaStack endpoint
LIGHTRAIL_LLAMA_STACK_TLS_SERVICE_CA_CERT_PATH  # TLS certificate
MYAPP_MODEL_ID                          # Model identifier
```

### API Changes

#### `/generate` Endpoint

**Request** (unchanged):
```json
{
  "prompt": "Show me some movies",
  "data": null,                    // Optional: inline data
  "skip_filtering": false          // Optional: skip smart filtering
}
```

**Response** (enhanced):
```json
{
  "response": {
    "component": "set-of-cards",
    "title": "Movies",
    "fields": [
      {
        "id": "default_data-movie_title",
        "name": "Title",
        "data_path": "$..default_data[*].movie.title",
        "data": ["Toy Story", "The Shawshank Redemption", ...]
      }
    ]
  },
  "metadata": {
    "model": {
      "model_id": "RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic",
      "base_url": "http://llamastack:5002"
    },
    "data_source": {
      "tool_name": "default_data",
      "data_size_bytes": 4237
    },
    "agent_events": [...]
  }
}
```

## Files Updated

### Root Level
- ✅ `README.md` - Updated with Lightrail/LlamaStack info
- ✅ `pyproject.toml` - Updated dependencies to 0.3.0+
- ✅ `poetry.lock` - Regenerated with new versions
- ✅ `llamastack.yaml` - Lightrail configuration
- ✅ `catalog-info.yaml` - Backstage catalog
- ✅ `main.sh` - Entrypoint script

### Parent Directory
- ✅ `tests/ngui-e2e/README.md` - Updated with Lightrail architecture

## Testing

### Health Check
```bash
curl http://localhost:8080/api/v1/health
```

Expected:
```json
{
  "status": "ok",
  "model": "RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic",
  "base_url": "http://llamastack:5002"
}
```

### Generate with Default Data
```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me some movies"}'
```

Expected: Component with 6 movies from `movies_data.json`

### Generate with Inline Data
```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me these products",
    "data": [
      {"name": "Laptop", "price": 999},
      {"name": "Mouse", "price": 29}
    ]
  }'
```

Expected: Component with custom product data

## Deployment

### Lightrail Local

```bash
# Build
lightrail-local-cli build

# Start
lightrail-local-cli start

# Check logs
lightrail-local-cli logs

# Stop
lightrail-local-cli stop
```

### Lightrail Production

Deployment is handled via GitLab CI/CD pipeline configured in the parent repository.

## Troubleshooting

### Issue: Empty Data Arrays

**Symptom**: Component generates but all `data` arrays are empty.

**Cause**: Using `next-gen-ui-llama-stack` 0.2.x

**Fix**: Upgrade to 0.3.0+
```bash
poetry add "next-gen-ui-llama-stack>=0.3.0" "next-gen-ui-agent>=0.3.0"
poetry update
```

### Issue: `ModuleNotFoundError: No module named 'llama_stack_client.types.agents'`

**Cause**: `llama-stack-client` 0.3.x has breaking changes

**Fix**: Pin to 0.2.x
```toml
"llama-stack-client (>=0.2.15,<0.3.0)"
```

### Issue: Import Errors in Docker

**Cause**: Relative imports don't work in Docker container

**Fix**: Use `app.` prefix for all imports:
```python
# ❌ Bad
from models import ErrorCode

# ✅ Good
from app.models import ErrorCode
```

## Migration Checklist

- [x] Copy all files from `ngui-e2e-testing/app/` to `next-gen-ui-agent/tests/ngui-e2e/server/app/`
- [x] Update dependencies to 0.3.0+ in `pyproject.toml`
- [x] Update `README.md` files
- [x] Add new features (default data, filtering, prompts)
- [x] Test all endpoints
- [x] Verify data arrays are populated
- [x] Document version requirements
- [x] Create migration summary

## Summary

The migration successfully adapted the NGUI E2E server from LangGraph to LlamaStack/Lightrail while:
- ✅ Maintaining the modular architecture
- ✅ Adding new features (default data, smart filtering)
- ✅ Improving error handling
- ✅ Ensuring compatibility with Lightrail deployment
- ✅ Fixing version compatibility issues (0.3.0+)

All functionality is working correctly with populated data arrays and proper metadata tracking.


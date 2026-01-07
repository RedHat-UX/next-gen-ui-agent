# Lightrail API with Next Gen UI Agent

FastAPI server with **Next Gen UI Agent** integration for AI-powered UI component generation using LlamaStack.

## Features

✅ **AI-Powered UI Generation** - Generate rich UI components from natural language  
✅ **Multiple Component Types** - Cards, tables, videos, images, set-of-cards  
✅ **Simple Movie Search** - JSON-based movie database with smart search  
✅ **LlamaStack Integration** - Enterprise LLM with SSL support  
✅ **CORS-Enabled** - Ready for frontend integration  

## Quick Start

```bash
# 1. Install dependencies
poetry install

# 2. Set environment variables
export LIGHTRAIL_LLAMA_STACK_BASE_URL="your-llama-stack-url"
export MYAPP_MODEL_ID="your-model-id"

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

**Request:**
```json
{
  "prompt": "Show me Toy Story details"
}
```

**Response:**
```json
{
  "response": {
    "component": "one-card",
    "title": "Toy Story",
    "fields": [...],
    "image": "https://..."
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

Add more in `app/movies_data.json`

## Supported Components

- `one-card` - Single item with image and fields
- `table` - Tabular data (multiple rows)
- `video-player` - Video/trailer playback
- `image` - Image display
- `set-of-cards` - Multiple card items

## Architecture

```
User Prompt → Movie Search → NGUI Agent + LLM → UI Component JSON
```

**Key Components:**
- `search_movies()` - Simple JSON-based search
- `NextGenUILlamaStackAgent` - LLM-powered component selection
- Manual `ToolStep` creation - Simulates agent tool execution

## Configuration Notes

**Enable All Components:**
```python
config = {
    "unsupported_components": True  # Enables table & set-of-cards
}
```

By default, NGUI Agent only enables `one-card`, `video-player`, and `image`. Set `unsupported_components: True` to access `table` and `set-of-cards`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LIGHTRAIL_LLAMA_STACK_BASE_URL` | LlamaStack server URL |
| `LIGHTRAIL_LLAMA_STACK_TLS_CA_CERT_PATH` | SSL certificate path |
| `MYAPP_MODEL_ID` | Model identifier |

## Example Prompts

```bash
# Get a card
curl -X POST http://localhost:8080/generate \
  -d '{"prompt": "Tell me about Inception"}'

# Get a table
curl -X POST http://localhost:8080/generate \
  -d '{"prompt": "Show all movies in a table"}'

# Get a video
curl -X POST http://localhost:8080/generate \
  -d '{"prompt": "Play Toy Story trailer"}'
```

## Development

**Add movies:** Edit `app/movies_data.json`  
**Modify search:** Update `search_movies()` in `app/main.py`  
**Change components:** Adjust config in `get_ngui_agent()`

---

Built with [Next Gen UI Agent](https://github.com/RedHat-UX/next-gen-ui-agent)

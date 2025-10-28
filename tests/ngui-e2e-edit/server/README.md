# NGUI E2E Server

[![Module Category](https://img.shields.io/badge/Module%20Category-Testing/Evaluation-darkmagenta)](https://github.com/RedHat-UX/next-gen-ui-agent)
[![Module Status](https://img.shields.io/badge/Module%20Status-Tech%20Preview-orange)](https://github.com/RedHat-UX/next-gen-ui-agent)

This module is part of the [Next Gen UI Agent project](https://github.com/RedHat-UX/next-gen-ui-agent).

FastAPI backend server for the NGUI end-to-end testing application. Provides AI-powered UI generation APIs using LangGraph integration with configurable AI models.

## Provides

* FastAPI server with NGUI agent integration
* LangGraph-based AI workflow for UI component generation
* Configurable AI model support (Ollama, OpenAI, models.corp)
* RESTful API endpoints for UI generation
* CORS-enabled for frontend integration

## Installation

### Prerequisites

1. **Install Ollama** (required for local AI model inference):
   ```bash
   # Visit: https://ollama.com/download
   # Pull the required model for this demo
   ollama pull llama3.2:3b
   ```

2. **Set up Python environment** (from project root directory):
   ```bash
   pants export
   # change `3.12.11` in the path to your python version, or to `latest` for venv symlink created from `CONTRIBUTING.md`!
   source dist/export/python/virtualenvs/python-default/3.12.11/bin/activate
   export PYTHONPATH=./libs:./tests:$PYTHONPATH
   ```

### Dependencies

The server uses dependencies managed by Pants build system. All required dependencies are automatically resolved from the source code.

## Configuration

The server supports multiple AI model configurations:

- **Ollama** (default): Local AI model inference
- **OpenAI**: Cloud-based AI model inference  
- **models.corp**: Corporate AI model inference

### Environment Variables

Configure the server using the following environment variables:

- `LLM_MODEL`: The AI model to use (default: "llama3.2:3b")
- `LLM_BASE_URL`: The base URL for the AI model API (default: "http://localhost:11434/v1")
- `LLM_API_KEY`: API key for models.corp and other providers that require authentication (optional)

**Quick Setup**: Copy `.env.sample` to `.env` and update the values:
```bash
cp .env.sample .env
# Edit .env with your configuration
```

### Example Configuration

For **Ollama** (local):
```bash
export LLM_MODEL="llama3.2:3b"
export LLM_BASE_URL="http://localhost:11434/v1"
```

For **models.corp**:
```bash
export LLM_MODEL="your-model-name"
export LLM_BASE_URL="https://models.corp/api/v1"
export LLM_API_KEY="your-api-key"
```

For **OpenAI**:
```bash
export LLM_MODEL="gpt-3.5-turbo"
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="your-openai-api-key"
```

## Running

### Start Ollama Service

First, ensure Ollama is running (required for AI model inference):

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/tags > /dev/null
if [ $? -ne 0 ]; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 3  # Wait for Ollama to start
fi

# Pull required model if not already available
ollama pull llama3.2:3b
```

### Start the Server

```bash
cd tests/ngui-e2e/server
uvicorn main:app --reload
```

The server will be available at:
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Base URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API Endpoints

- `POST /generate` - Generate UI components based on user prompts
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /openapi.json` - OpenAPI specification

## Troubleshooting

### Common Issues

**1. CORS Error: "Access to fetch blocked by CORS policy"**
- **Cause**: Ollama is not running or the backend crashed before sending CORS headers
- **Solution**: Ensure Ollama is running first with `ollama serve`, then restart the backend

**2. API Connection Error: "Connection refused"**
- **Cause**: Ollama service stopped or not accessible on port 11434
- **Solution**: Start Ollama with `ollama serve` and verify it's running with `curl http://localhost:11434/api/tags`

**3. Backend 500 Error: "No data transformer found for component"**
- **Cause**: LLM generated invalid component names
- **Solution**: This is typically resolved by ensuring Ollama is properly running and the model is loaded

### Verification Steps

```bash
# Check Ollama is running
curl -s http://localhost:11434/api/tags

# Check backend is running
curl -I http://localhost:8000/docs

# Test API endpoint
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"prompt": "Tell me about Toy Story"}'
```

## Port Configuration

- **Server runs on**: `localhost:8000`
- **Ollama runs on**: `localhost:11434`

## Links

* [Documentation](https://redhat-ux.github.io/next-gen-ui-agent/)
* [Source Codes](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/tests/ngui-e2e/server)
* [Contributing](https://redhat-ux.github.io/next-gen-ui-agent/development/contributing/)

# NGUI End-to-End Testing Application

This directory contains a complete end-to-end testing application for the Next Gen UI (NGUI) system, demonstrating AI-driven UI component generation with a split server/client architecture.

## Technology Stack

### Server
- **Framework**: FastAPI
- **AI Integration**: The server supports **two modes**:
  - **Lightrail / LlamaStack** — LlamaStack (via `next-gen-ui-llama-stack` 0.3.0+), e.g. Red Hat's Lightrail platform; model such as Llama 3.3 70B Instruct.
  - **Local / direct LLM** — Any OpenAI-compatible API (Ollama, Gemini, Red Hat models.corp, etc.) via LangGraph + ChatOpenAI; no Lightrail required.
- **Language**: Python 3.12+

### Client
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Components**: PatternFly / RHDS
- **State Management**: React Hooks

## Structure

```
ngui-e2e/
├── server/           # FastAPI backend with NGUI agent (Lightrail/LlamaStack or local/direct LLM)
└── client/           # React frontend application
```

## Components

- **`server/`** - FastAPI backend that provides AI-powered UI generation APIs. Supports **Lightrail/LlamaStack** (deployed) or **local/direct LLM** (Ollama, Gemini, models.corp, etc.); see Quick Start below.
- **`client/`** - React frontend application that consumes the backend APIs and renders dynamic UI components

## Architecture

### Server (Backend)

The server uses a **modular architecture** with the following components:

- **LLM modes**: Either **LlamaStack** (e.g. Lightrail deployment) or **local/direct LLM** (OpenAI-compatible API). Mode is chosen via environment variables; see [server/README.md](server/README.md).
- **LlamaStack**: Uses `next-gen-ui-llama-stack` adapter (0.3.0+) when `LLAMA_STACK_BASE_URL` is set.
- **Lightrail**: Optional containerized deployment using Red Hat's Lightrail platform.
- **Modular Structure**:
  - `agents/` - NGUI agent configuration
  - `data_sources/` - Data handling (inline, default, filtering)
  - `routes/` - API endpoints (`/generate`, `/health`, `/wdyk`)
  - `utils/` - Helper functions (validation, logging, response formatting)
  - `models.py` - Pydantic models for request/response
  - `config.py` - Configuration and environment setup
  - `llm.py` - LLM client (LlamaStack or local/direct)

### Key Features

✅ **Default Data Fallback** - Automatically uses `movies_data.json` when no inline data is provided  
✅ **Inline Custom Data** - Support for custom JSON data in POST requests  
✅ **Smart Filtering Agent** - Intelligent data filtering based on user prompts  
✅ **Component Generation** - Generates UI components (set-of-cards, table, one-card, etc.)  
✅ **Metadata Tracking** - Detailed metadata about model, data source, and agent events  
✅ **Error Handling** - Standardized error responses with error codes and suggestions  

## Getting Started

Each subfolder contains its own README with detailed setup, installation, configuration, and running instructions:

- See [`server/README.md`](server/README.md) for backend setup, Lightrail deployment, and configuration
- See [`client/README.md`](client/README.md) for frontend setup and configuration

## Quick Start

### Server (Lightrail)

```bash
cd server
lightrail-local-cli build
lightrail-local-cli start
```

The server will be available at `http://localhost:8080`

### Server (direct LLM)

You can run the server against a direct LLM (Ollama, Gemini, or any OpenAI-compatible API) instead of Lightrail. Configure `LLM_MODEL`, `LLM_BASE_URL`, and optionally `LLM_API_KEY` in the server’s `.env` (see [server/README.md](server/README.md)).

**Option: Red Hat model access** — For direct access to Red Hat-hosted models (e.g. for development or demos), you can use [developer.models.corp.redhat.com](https://developer.models.corp.redhat.com/). **VPN is required** to reach models.corp. You can request **21 days of access** by submitting a ticket in Red Hat Hub: [Request access](https://redhathub.service-now.com/hub?id=sc_cat_item&sys_id=882ad1b71bebd610b6ccea45624bcb3d). Use the provided base URL and API key in the server’s `.env` for `LLM_BASE_URL` and `LLM_API_KEY`.

### Client

```bash
cd client
npm install
npm run dev
```

The client will be available at `http://localhost:5173`

## API Endpoints

- `POST /generate` - Generate UI components from prompts
- `GET /api/v1/health` - Health check
- `GET /api/v1/wdyk` - What Do You Know (available data sources)

## Purpose

This application serves as a comprehensive testing and demonstration platform for the NGUI system, allowing contributors to understand the complete workflow from AI model inference to dynamic UI component rendering. Run it with **Lightrail** (production-like) or with a **local/direct LLM** (Ollama, Gemini, models.corp, etc.) for development.

## Version Compatibility

**Important**: This server requires:
- `next-gen-ui-agent` >= 0.3.0
- `next-gen-ui-llama-stack` >= 0.3.0
- `llama-stack-client` >= 0.2.15, < 0.3.0

Version 0.2.x had issues with empty data arrays in generated components. Always use 0.3.0+.

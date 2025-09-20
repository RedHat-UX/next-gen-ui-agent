# NGUI: End-to-End Demo Application

## ✨ Summary

This is a complete end-to-end example of the Next Gen UI (NGUI) system with **split server/client architecture**. The application demonstrates AI-driven UI component generation using FastAPI backend and React frontend, making it easier for contributors to understand the full NGUI workflow.

---

## 🏗️ Architecture Overview

```
ngui-e2e/
├── server/           # FastAPI backend with NGUI agent
│   ├── main.py      # API server with LangGraph integration
│   └── BUILD        # Pants build configuration
└── client/          # React frontend application
    ├── src/         # React components and hooks
    ├── package.json # Frontend dependencies
    └── vite.config.ts # Build configuration
```

## 📋 Recent Changes

- **Split Architecture**: Separated backend (`server/`) and frontend (`client/`) for better deployment flexibility
- **Enhanced Documentation**: Complete setup instructions for both server and client components
- **Configurable Backend**: The `server/main.py` supports different AI models (Ollama, OpenAI, models.corp)
- **React Frontend**: Vite-based React app with `OneCard` component demo and ChatBot interface
- **Deployment Ready**: Prepared for Lightrail (backend) + SSR/Vercel (frontend) deployment

---

## ⚡ Quick Start

For experienced users, here's the essential command sequence:

```bash
# 1. Check/Start Ollama
ollama serve &  # Start in background if not running
ollama pull llama3.2:3b  # Ensure model is available (updated model)

# 2. Start Backend API (from ngui-e2e directory)
cd server
uvicorn main:app --reload

# 3. Start Frontend (in another terminal, from ngui-e2e directory)
cd client
npm install && npm run dev
```

---

## 🧪 Detailed Setup Instructions

Follow these steps to test the complete chat, AI, and UI generation flow:

1.  **Install Ollama**:

```bash
# Install Ollama if not already installed
# Visit: https://ollama.com/download

# Pull the required model for this demo
ollama pull llama3.2:3b
```

2.  **Start the Backend**:

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

Set up Python environment in project root directory:

```bash
pants export
# change `3.12.11` in the path to your python version, or to `latest` for venv symlink created from `CONTRIBUTING.md`!
source dist/export/python/virtualenvs/python-default/3.12.11/bin/activate
export PYTHONPATH=./libs:./tests:$PYTHONPATH
```

Start the API server:

```bash
cd tests/ngui-e2e/server
uvicorn main:app --reload
```

You can check it's running under [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3.  **Start the Frontend**:

Navigate to the `client` folder and run:

```bash
cd tests/ngui-e2e/client
npm install
npm link dynamicui
npm run dev
```

Note: It's expected you already build `dynamicui` package located in [libs_js/next_gen_ui_react](/libs_js/next_gen_ui_react/)

---

## 🚀 Benefits

- **Easy Setup**: New contributors can now get up and running quickly.
- **Flexible Configuration**: The system is more adaptable, allowing for different AI models to be used.
- **Complete Working Example**: Provides a clear, functional reference for the entire NGUI system.
- **Clear Documentation**: The improved documentation simplifies the setup and testing process.

---

## 🔧 Troubleshooting

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

**4. Port Conflicts**
- **Backend runs on**: `localhost:8000`
- **Frontend runs on**: `localhost:5173` (default Vite dev server)
- **Ollama runs on**: `localhost:11434`

### Verification Steps

```bash
# Check Ollama is running
curl -s http://localhost:11434/api/tags

# Check backend is running
curl -I http://localhost:8000/docs

# Test API endpoint
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"prompt": "Tell me about Toy Story"}'
```

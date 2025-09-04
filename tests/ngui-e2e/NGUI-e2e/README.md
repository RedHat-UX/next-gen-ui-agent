# NGUI: End-to-End Demo

## ✨ Summary

This update introduces a complete end-to-end example of the Next Gen UI (NGUI) system, featuring a new demo, improved configuration, and comprehensive documentation. This makes it easier for new contributors to get started and provides a flexible foundation for development.

---

## 📋 Changes

- **New Demo**: Added a React Vite project with a `OneCard` component demo.
- **Enhanced Documentation**: The `README` now includes complete setup instructions for Ollama, the backend, and the frontend.
- **Configurable Backend**: The `main.py` file has been made more generic to support different AI models like Ollama, OpenAI, and others.
- **Configuration Guide**: A new `MODEL_CONFIGURATION.md` file provides detailed setup examples.
- **Fixed Imports**: Updated the `DynamicComponent` import to work correctly with the npm-linked UI package.

---

## ⚡ Quick Start

For experienced users, here's the essential command sequence:

```bash
# 1. Check/Start Ollama
ollama serve &  # Start in background if not running
ollama pull granite3-dense:8b  # Ensure model is available

# 2. Start Backend API
cd tests/ngui-e2e
uvicorn main:app --reload

# 3. Start Frontend (in another terminal)
cd tests/ngui-e2e/NGUI-e2e
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
ollama pull granite3-dense:8b
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
ollama pull granite3-dense:8b
```

Set up Python environment in project root directory:

```bash
pants export
# change `3.11.13` in the path to your python version, or to `latest` for venv symlink created from `CONTRIBUTING.md`!
source dist/export/python/virtualenvs/python-default/3.11.13/bin/activate
export PYTHONPATH=./libs:./tests:$PYTHONPATH
```

Start the API server:

```bash
cd tests/ngui-e2e
uvicorn main:app --reload
```

You can check it's running under [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3.  **Start the Frontend**:

Navigate to the `NGUI-e2e` folder and run:

```bash
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

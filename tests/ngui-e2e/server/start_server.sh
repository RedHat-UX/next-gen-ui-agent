#!/bin/bash
# Start the NGUI E2E server locally using the project's Pants-managed environment.
# Supports both local LLM (Ollama, Gemini) and LlamaStack; configure via .env (see .env.sample).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Project root (3 levels up from server directory)
PROJECT_ROOT="$(cd ../../.. && pwd)"

# Pants export virtualenv
VENV_DIR="$PROJECT_ROOT/dist/export/python/virtualenvs/python-default/latest"
PYTHON_BIN="$VENV_DIR/bin/python"
UVICORN_BIN="$VENV_DIR/bin/uvicorn"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "ERROR: Virtualenv not found at $VENV_DIR"
    echo "Please run 'pants export' from the project root first"
    exit 1
fi

if [ ! -f "$UVICORN_BIN" ]; then
    echo "ERROR: uvicorn not found at $UVICORN_BIN"
    echo "Please run 'pants export' from the project root first"
    exit 1
fi

echo "Using Python: $PYTHON_BIN"
echo "Using uvicorn: $UVICORN_BIN"

# PYTHONPATH so app can import libs and server modules
export PYTHONPATH="$PROJECT_ROOT/libs:$PROJECT_ROOT/tests:$PYTHONPATH"

# Load .env if present (for LLM_MODEL, LLM_BASE_URL, LLM_API_KEY or LlamaStack vars)
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "Loaded .env"
fi

echo "Starting server from: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo "Configure LLM via .env (see .env.sample for local vs LlamaStack)"
echo ""
exec "$PYTHON_BIN" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 --log-level info

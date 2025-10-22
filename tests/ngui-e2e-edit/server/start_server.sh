#!/bin/bash

# Navigate to the server directory first
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Get the project root (3 levels up from server directory)
PROJECT_ROOT="$(cd ../../.. && pwd)"

# Set up virtualenv paths
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

# Set the PYTHONPATH to include the libs and tests directories
export PYTHONPATH="$PROJECT_ROOT/libs:$PROJECT_ROOT/tests:$PYTHONPATH"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server
echo "Starting server from: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"
echo "PYTHONPATH: $PYTHONPATH"
echo "LLM_MODEL: $LLM_MODEL"
echo "LLM_BASE_URL: $LLM_BASE_URL"
echo ""
"$PYTHON_BIN" -m uvicorn main:app --reload


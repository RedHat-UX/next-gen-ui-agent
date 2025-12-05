#!/bin/bash
# Start the NGUI E2E server and client with proper environment setup

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

# Environment variables for LLM configuration
export LLM_MODEL="${LLM_MODEL:-qwen2.5:7b}"
export LLM_BASE_URL="${LLM_BASE_URL:-http://localhost:11434/v1}"
export LLM_API_KEY="${LLM_API_KEY:-}"

# Set PYTHONPATH to include libs and tests directories
export PYTHONPATH="${PROJECT_ROOT}/libs:${PROJECT_ROOT}/tests"

# Path to the Python virtual environment
PYTHON_BIN="${PROJECT_ROOT}/dist/export/python/virtualenvs/python-default/latest/bin/python"

# Cleanup function to kill background processes
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ -n "$SERVER_PID" ]; then
        kill "$SERVER_PID" 2>/dev/null
        echo "Backend server stopped"
    fi
    if [ -n "$CLIENT_PID" ]; then
        kill "$CLIENT_PID" 2>/dev/null
        echo "Frontend client stopped"
    fi
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup INT TERM

echo "Starting NGUI E2E Test Environment"
echo "=================================="
echo ""

# Start the backend server
echo "Starting backend server on http://127.0.0.1:8000..."
cd "$PROJECT_ROOT"
"$PYTHON_BIN" -m uvicorn tests.ngui-e2e.server.main:app --reload &
SERVER_PID=$!

# Give server time to start
sleep 2

# Start the frontend client
echo "Starting frontend client on http://localhost:5173..."
cd "$PROJECT_ROOT/tests/ngui-e2e/client"
npm run dev &
CLIENT_PID=$!

echo ""
echo "Services started:"
echo "  Backend API:    http://127.0.0.1:8000"
echo "  API Docs:       http://127.0.0.1:8000/docs"
echo "  Frontend:       http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for any process to exit
wait

#!/usr/bin/env fish
# Start the NGUI E2E server and client with proper environment setup

# Get the absolute path to the project root
set PROJECT_ROOT (cd (dirname (status -f))/../../..; and pwd)

# Environment variables for LLM configuration
set -x LLM_MODEL (test -n "$LLM_MODEL"; and echo $LLM_MODEL; or echo "qwen2.5:7b")
set -x LLM_BASE_URL (test -n "$LLM_BASE_URL"; and echo $LLM_BASE_URL; or echo "http://localhost:11434/v1")
set -x LLM_API_KEY (test -n "$LLM_API_KEY"; and echo $LLM_API_KEY; or echo "")

# Set PYTHONPATH to include libs and tests directories
set -x PYTHONPATH "$PROJECT_ROOT/libs:$PROJECT_ROOT/tests"

# Path to the Python virtual environment
set PYTHON_BIN "$PROJECT_ROOT/dist/export/python/virtualenvs/python-default/latest/bin/python"

# Cleanup function to kill background processes
function cleanup
    echo ""
    echo "Shutting down services..."
    if test -n "$SERVER_PID"
        kill $SERVER_PID 2>/dev/null
        echo "Backend server stopped"
    end
    if test -n "$CLIENT_PID"
        kill $CLIENT_PID 2>/dev/null
        echo "Frontend client stopped"
    end
    exit 0
end

# Set up trap to cleanup on script exit
trap cleanup INT TERM

echo "Starting NGUI E2E Test Environment"
echo "=================================="
echo ""

# Start the backend server
echo "Starting backend server on http://127.0.0.1:8000..."
cd "$PROJECT_ROOT"
$PYTHON_BIN -m uvicorn tests.ngui-e2e.server.main:app --reload &
set -g SERVER_PID $last_pid

# Give server time to start
sleep 2

# Start the frontend client
echo "Starting frontend client on http://localhost:5173..."
cd "$PROJECT_ROOT/tests/ngui-e2e/client"
npm run dev &
set -g CLIENT_PID $last_pid

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

#!/bin/bash

# Set the PYTHONPATH to include the next-gen-ui-agent libs directory
export PYTHONPATH="/Users/hrithikgavankar/Desktop/WORK/NGUI_MAIN_PROD/E2E-Project/next-gen-ui-agent/libs:$PYTHONPATH"

# Navigate to the server directory
cd "$(dirname "$0")"

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the server
echo "Starting server with PYTHONPATH: $PYTHONPATH"
echo "LLM_MODEL: $LLM_MODEL"
echo "LLM_BASE_URL: $LLM_BASE_URL"
uvicorn main:app --reload


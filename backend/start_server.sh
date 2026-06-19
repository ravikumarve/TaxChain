#!/bin/bash

# TaxChain Backend Startup Script
# This script ensures the backend runs with the correct virtual environment

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Check if slowapi is installed, if not install it
if ! python -c "import slowapi" 2>/dev/null; then
    echo "Installing missing dependencies..."
    pip install slowapi aiosqlite
fi

# Start the server
echo "Starting TaxChain Backend API..."
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
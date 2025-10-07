#!/bin/bash
# Script to run the POS Pipeline API server

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration before running in production!"
fi

# Create necessary directories
mkdir -p logs storage/videos storage/models

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Starting POS Pipeline API Server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
python -m uvicorn services.api_gateway.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
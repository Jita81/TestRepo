#!/bin/bash
# Script to run tests for the POS Pipeline

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create necessary directories
mkdir -p logs storage/videos storage/models

echo "Running POS Pipeline Test Suite..."
echo ""

# Run tests with coverage
pytest -v \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-config=.coveragerc \
    "$@"

echo ""
echo "Coverage report generated in htmlcov/index.html"
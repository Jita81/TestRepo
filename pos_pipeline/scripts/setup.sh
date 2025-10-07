#!/bin/bash
# Setup script for POS Pipeline

set -e

echo "========================================="
echo "POS Pipeline Setup"
echo "========================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo "Error: Python 3.11 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take 10-15 minutes..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Create .env file
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "⚠️  Please edit .env and set a secure API_KEY!"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create directories
echo "Creating required directories..."
mkdir -p logs
mkdir -p storage/videos
mkdir -p storage/models
echo "✓ Directories created"
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.sh
echo "✓ Scripts are executable"
echo ""

# Run tests
echo "Running tests to verify installation..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest --quiet --tb=short

echo ""
echo "========================================="
echo "Setup Complete! ✓"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Review and edit .env file"
echo "  2. Run: ./scripts/run_server.sh"
echo "  3. Visit: http://localhost:8000/docs"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
#!/bin/bash

# Start GitHub to App Converter with Dashboard
# This script starts the server and opens the dashboard in your default browser

echo "🚀 Starting GitHub to App Converter..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing required dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ Starting server on http://localhost:8000"
echo "📊 Dashboard will be available at http://localhost:8000/dashboard"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py
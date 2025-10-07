#!/bin/bash
echo "Starting Node.js application..."

# Install dependencies if package.json exists
if [ -f package.json ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Start the application
if [ -f package.json ]; then
    npm start
else
    echo "No package.json found. Available files:"
    ls -la
fi

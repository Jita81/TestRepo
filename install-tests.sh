#!/bin/bash

# Todo App - Test Suite Installation Script
# This script installs all dependencies needed to run the Playwright tests

set -e

echo "════════════════════════════════════════════════════════════"
echo "  Todo App - Test Suite Installation"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js version 18+ is required"
    echo "Current version: $(node -v)"
    echo "Please upgrade Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"
echo "✅ npm version: $(npm -v)"
echo ""

# Install dependencies
echo "📦 Installing npm dependencies..."
npm install

echo ""
echo "🌐 Installing Playwright browsers..."
npx playwright install

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ Installation Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 Quick Start:"
echo ""
echo "  Run all tests:"
echo "    npm test"
echo ""
echo "  Run tests in UI mode:"
echo "    npm run test:ui"
echo ""
echo "  View test report:"
echo "    npm run test:report"
echo ""
echo "📚 Documentation:"
echo "  - README_TESTS.md       - Complete testing guide"
echo "  - QUICK_REFERENCE.md    - Quick command reference"
echo "  - TEST_SUMMARY.md       - Test suite overview"
echo ""
echo "════════════════════════════════════════════════════════════"
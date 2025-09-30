#!/bin/bash

# Todo App - Test Execution Script
# Quick script to run tests with common options

set -e

show_help() {
    echo "Todo App - Test Execution Script"
    echo ""
    echo "Usage: ./run-tests.sh [option]"
    echo ""
    echo "Options:"
    echo "  all         - Run all tests (default)"
    echo "  ui          - Run tests in UI mode"
    echo "  headed      - Run tests in headed mode"
    echo "  debug       - Run tests in debug mode"
    echo "  chromium    - Run tests in Chromium only"
    echo "  firefox     - Run tests in Firefox only"
    echo "  webkit      - Run tests in WebKit (Safari) only"
    echo "  mobile      - Run mobile tests only"
    echo "  report      - Show test report"
    echo "  help        - Show this help"
    echo ""
    echo "Examples:"
    echo "  ./run-tests.sh"
    echo "  ./run-tests.sh ui"
    echo "  ./run-tests.sh chromium"
}

case "${1:-all}" in
    all)
        echo "Running all tests..."
        npm test
        ;;
    ui)
        echo "Running tests in UI mode..."
        npm run test:ui
        ;;
    headed)
        echo "Running tests in headed mode..."
        npm run test:headed
        ;;
    debug)
        echo "Running tests in debug mode..."
        npm run test:debug
        ;;
    chromium)
        echo "Running Chromium tests..."
        npm run test:chromium
        ;;
    firefox)
        echo "Running Firefox tests..."
        npm run test:firefox
        ;;
    webkit)
        echo "Running WebKit tests..."
        npm run test:webkit
        ;;
    mobile)
        echo "Running mobile tests..."
        npm run test:mobile
        ;;
    report)
        echo "Opening test report..."
        npm run test:report
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
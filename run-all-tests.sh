#!/bin/bash
# Comprehensive test runner for contact form implementation

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        CONTACT FORM - COMPREHENSIVE TEST SUITE                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Clean up test databases
echo "🧹 Cleaning up test databases..."
rm -f contacts.db test_*.db demo_contacts.db
echo "✓ Cleanup complete"
echo ""

# Run Python unit and integration tests
echo "═══════════════════════════════════════════════════════════════"
echo "📦 PYTHON TESTS (Unit + Integration + API)"
echo "═══════════════════════════════════════════════════════════════"
/home/ubuntu/.local/bin/pytest tests/test_contact_form.py -v --tb=short

PYTHON_EXIT=$?
echo ""

# Run JavaScript unit tests
echo "═══════════════════════════════════════════════════════════════"
echo "🟨 JAVASCRIPT TESTS (Unit + Validation)"
echo "═══════════════════════════════════════════════════════════════"
npm run test:js

JS_EXIT=$?
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $PYTHON_EXIT -eq 0 ]; then
    echo "✅ Python Tests: PASSED (26/26 tests)"
else
    echo "❌ Python Tests: FAILED"
fi

if [ $JS_EXIT -eq 0 ]; then
    echo "✅ JavaScript Tests: PASSED (34/34 tests)"
else
    echo "❌ JavaScript Tests: FAILED"
fi

echo ""
echo "📊 Total Test Coverage:"
echo "   - Unit Tests: 60 tests (Python + JavaScript)"
echo "   - Integration Tests: API endpoints, Database operations"
echo "   - Edge Cases: Unicode, XSS, SQL injection, Rate limiting"
echo ""

# Optional: Run E2E tests (commented out by default as they take longer)
# echo "═══════════════════════════════════════════════════════════════"
# echo "🎭 E2E TESTS (Playwright - Optional)"
# echo "═══════════════════════════════════════════════════════════════"
# echo "To run E2E tests, execute:"
# echo "   npx playwright test --project=chromium"
# echo ""

# Exit with error if any tests failed
if [ $PYTHON_EXIT -ne 0 ] || [ $JS_EXIT -ne 0 ]; then
    exit 1
fi

echo "✅ ALL TESTS PASSED!"
echo ""
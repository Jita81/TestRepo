#!/usr/bin/env python3
"""
Comprehensive Test Runner for Contact Form Component

Runs all test suites:
1. Unit tests (validation logic)
2. Integration tests (API endpoints)
3. E2E tests (complete workflows)
4. Security tests

Usage:
    python3 run_all_tests.py
    python3 run_all_tests.py --verbose
    python3 run_all_tests.py --suite unit
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def run_test_file(filepath, test_name, verbose=False):
    """Run a single test file and return results"""
    print(f"\n{Colors.OKBLUE}Running {test_name}...{Colors.ENDC}")
    print("-" * 60)
    
    try:
        # Check if pytest is available
        try:
            import pytest
            has_pytest = True
        except ImportError:
            has_pytest = False
        
        if has_pytest and filepath.endswith('.py') and 'test_' in filepath:
            # Run with pytest if available
            args = [sys.executable, "-m", "pytest", filepath, "-v" if verbose else "-q"]
            result = subprocess.run(args, capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success(f"{test_name} PASSED")
                if verbose:
                    print(result.stdout)
                return True
            else:
                print_error(f"{test_name} FAILED")
                print(result.stdout)
                print(result.stderr)
                return False
        else:
            # Run directly with python
            result = subprocess.run([sys.executable, filepath], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success(f"{test_name} PASSED")
                if verbose:
                    print(result.stdout)
                return True
            else:
                print_error(f"{test_name} FAILED")
                print(result.stdout)
                print(result.stderr)
                return False
                
    except Exception as e:
        print_error(f"Error running {test_name}: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")
    
    dependencies = {
        'pytest': 'pip install pytest',
        'httpx': 'pip install httpx (for FastAPI TestClient)',
        'fastapi': 'pip install fastapi',
    }
    
    missing = []
    
    for package, install_cmd in dependencies.items():
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_warning(f"{package} is NOT installed - {install_cmd}")
            missing.append(package)
    
    if missing:
        print_info(f"\nSome tests may be skipped due to missing dependencies")
        print_info(f"To install all: pip install pytest httpx fastapi")
    
    return len(missing) == 0


def run_all_tests(verbose=False, suite=None):
    """Run all test suites"""
    print_header("Contact Form Component - Comprehensive Test Suite")
    
    # Check dependencies
    all_deps = check_dependencies()
    
    # Define test suites
    test_suites = {
        'unit': ('tests/test_unit_validation.py', 'Unit Tests (Validation Logic)'),
        'integration': ('tests/test_integration_api.py', 'Integration Tests (API Endpoints)'),
        'e2e': ('tests/test_e2e_workflows.py', 'E2E Tests (User Workflows)'),
        'security': ('test_security.py', 'Security Tests'),
    }
    
    # Filter by suite if specified
    if suite:
        if suite not in test_suites:
            print_error(f"Unknown test suite: {suite}")
            print_info(f"Available suites: {', '.join(test_suites.keys())}")
            return False
        test_suites = {suite: test_suites[suite]}
    
    # Run tests
    results = {}
    total_passed = 0
    total_failed = 0
    
    for suite_name, (filepath, description) in test_suites.items():
        print_header(description)
        
        if os.path.exists(filepath):
            passed = run_test_file(filepath, description, verbose)
            results[suite_name] = passed
            
            if passed:
                total_passed += 1
            else:
                total_failed += 1
        else:
            print_warning(f"Test file not found: {filepath}")
            results[suite_name] = None
    
    # Print summary
    print_header("Test Summary")
    
    for suite_name, result in results.items():
        suite_info = test_suites.get(suite_name, (None, suite_name))[1]
        if result is True:
            print_success(f"{suite_info}")
        elif result is False:
            print_error(f"{suite_info}")
        else:
            print_warning(f"{suite_info} (SKIPPED)")
    
    print(f"\n{Colors.BOLD}Total: {total_passed} passed, {total_failed} failed{Colors.ENDC}")
    
    # Final verdict
    if total_failed == 0 and total_passed > 0:
        print_success("\n🎉 All tests passed!")
        return True
    elif total_failed > 0:
        print_error(f"\n⚠️  {total_failed} test suite(s) failed")
        return False
    else:
        print_warning("\n⚠️  No tests were run")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run comprehensive test suite for contact form component'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--suite', '-s',
        choices=['unit', 'integration', 'e2e', 'security'],
        help='Run specific test suite only'
    )
    
    args = parser.parse_args()
    
    success = run_all_tests(verbose=args.verbose, suite=args.suite)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

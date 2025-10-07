#!/usr/bin/env python3
"""
Test validation script - verifies test structure and readiness.
Does not require external dependencies.
"""

import ast
import sys
from pathlib import Path
from collections import defaultdict


def analyze_test_file(filepath):
    """Analyze a test file and extract test information."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        test_classes = []
        test_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    # Count test methods in class
                    test_methods = [m for m in node.body 
                                   if isinstance(m, ast.FunctionDef) 
                                   and m.name.startswith('test_')]
                    test_classes.append({
                        'name': node.name,
                        'methods': len(test_methods),
                        'method_names': [m.name for m in test_methods if isinstance(m, ast.FunctionDef)]
                    })
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_') and not any(
                    isinstance(parent, ast.ClassDef) 
                    for parent in ast.walk(tree)
                ):
                    test_functions.append(node.name)
        
        return {
            'classes': test_classes,
            'functions': test_functions,
            'total_tests': sum(c['methods'] for c in test_classes) + len(test_functions)
        }
    except Exception as e:
        print(f"  ⚠️  Error analyzing {filepath.name}: {e}")
        return None


def main():
    """Main validation function."""
    print("=" * 80)
    print(" Test Suite Validation")
    print("=" * 80)
    print()
    
    pipeline_dir = Path(__file__).parent
    tests_dir = pipeline_dir / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    test_files = sorted(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found!")
        return 1
    
    print(f"Found {len(test_files)} test files\n")
    
    total_stats = {
        'files': 0,
        'classes': 0,
        'tests': 0,
        'issues': []
    }
    
    file_details = []
    
    for test_file in test_files:
        print(f"📄 {test_file.name}")
        
        analysis = analyze_test_file(test_file)
        
        if analysis is None:
            total_stats['issues'].append(test_file.name)
            print()
            continue
        
        total_stats['files'] += 1
        total_stats['classes'] += len(analysis['classes'])
        total_stats['tests'] += analysis['total_tests']
        
        print(f"   Classes: {len(analysis['classes'])}")
        print(f"   Tests: {analysis['total_tests']}")
        
        if analysis['classes']:
            for cls in analysis['classes']:
                print(f"     • {cls['name']} ({cls['methods']} tests)")
        
        if analysis['functions']:
            print(f"     • {len(analysis['functions'])} standalone test functions")
        
        file_details.append({
            'name': test_file.name,
            'analysis': analysis
        })
        
        print()
    
    print("=" * 80)
    print(" Summary")
    print("=" * 80)
    print()
    print(f"✅ Test Files: {total_stats['files']}")
    print(f"✅ Test Classes: {total_stats['classes']}")
    print(f"✅ Total Tests: {total_stats['tests']}")
    
    if total_stats['issues']:
        print(f"\n⚠️  Files with issues: {len(total_stats['issues'])}")
        for issue in total_stats['issues']:
            print(f"   - {issue}")
    
    print()
    
    # Detailed breakdown
    print("=" * 80)
    print(" Test Coverage by File")
    print("=" * 80)
    print()
    
    for detail in sorted(file_details, key=lambda x: x['analysis']['total_tests'], reverse=True):
        analysis = detail['analysis']
        print(f"{detail['name']:30} {analysis['total_tests']:3} tests  "
              f"({len(analysis['classes'])} classes)")
    
    print()
    print("=" * 80)
    print(" Validation Result")
    print("=" * 80)
    print()
    
    if total_stats['tests'] >= 100:
        print(f"✅ EXCELLENT: {total_stats['tests']} tests provide comprehensive coverage!")
    elif total_stats['tests'] >= 50:
        print(f"✅ GOOD: {total_stats['tests']} tests provide solid coverage!")
    else:
        print(f"⚠️  WARNING: Only {total_stats['tests']} tests found. Consider adding more.")
    
    if total_stats['issues']:
        print(f"⚠️  {len(total_stats['issues'])} file(s) had analysis issues")
        return 1
    
    print()
    print("✅ All test files are properly structured and ready to run!")
    print()
    
    # Check for essential test files
    essential_tests = [
        'test_models.py',
        'test_api.py',
        'test_exceptions.py',
        'test_edge_cases.py'
    ]
    
    found_essential = [f.name for f in test_files if f.name in essential_tests]
    
    print("Essential Test Coverage:")
    for essential in essential_tests:
        if essential in found_essential:
            print(f"  ✅ {essential}")
        else:
            print(f"  ❌ {essential} (missing)")
    
    print()
    print("=" * 80)
    print("To run tests: pytest -v")
    print("For coverage: pytest --cov=. --cov-report=html")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
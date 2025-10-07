#!/usr/bin/env python
"""
Test runner script that ensures all tests pass.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run all tests and report results."""
    print("=" * 80)
    print("Running Pipeline Test Suite")
    print("=" * 80)
    print()
    
    # Change to pipeline directory
    pipeline_dir = Path(__file__).parent
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, "-m", "pytest",
        str(pipeline_dir / "tests"),
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
        "--color=yes"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=pipeline_dir)
    
    print()
    print("=" * 80)
    if result.returncode == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ TESTS FAILED (exit code: {result.returncode})")
    print("=" * 80)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
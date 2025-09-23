#!/usr/bin/env python3
"""
Build script for demo_app_2
"""

import os
import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build executable using PyInstaller."""
    try:
        # Install PyInstaller if not available
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Build executable
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "demo_app_2",
            "--add-data", ".:.",
            f"demo_app_2_wrapper.py"
        ]
        
        print("Building executable...")
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("Executable built successfully!")
            print(f"Find your executable in: dist/demo_app_2")
        else:
            print("Build failed!")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_executable()

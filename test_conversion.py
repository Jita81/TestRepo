#!/usr/bin/env python3
"""
Test script for GitHub to App Converter
"""

import requests
import json
import time
from pathlib import Path

def test_conversion():
    """Test the conversion functionality."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing GitHub to App Converter")
    print("=" * 50)
    
    # Test 1: Check if the web interface is accessible
    print("1. Testing web interface...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Web interface is accessible")
        else:
            print(f"❌ Web interface returned status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Failed to access web interface: {e}")
        return
    
    # Test 2: Test conversion with a simple repository
    print("\n2. Testing repository conversion...")
    
    # Use a simple, small repository for testing
    test_repo = "https://github.com/octocat/Hello-World"
    
    conversion_data = {
        "github_url": test_repo,
        "app_name": "test_app",
        "target_platform": "web"
    }
    
    try:
        print(f"   Converting repository: {test_repo}")
        response = requests.post(f"{base_url}/convert", data=conversion_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversion completed successfully!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            if 'download_url' in result:
                print(f"   Download URL: {result.get('download_url')}")
        elif response.status_code == 403:
            print("⚠️  GitHub API rate limit exceeded")
            print("   Please wait an hour or configure a GitHub token")
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   Details: {error_data['detail']}")
            except:
                pass
        elif response.status_code == 422:
            print("❌ Invalid repository URL or request data")
            try:
                error_data = response.json()
                print(f"   Details: {error_data}")
            except:
                pass
        else:
            print(f"❌ Conversion failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Conversion timed out (this is normal for large repositories)")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Network connection error: {e}")
        print("   Make sure the server is running and accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from server")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\nTo use the application:")
    print("1. Open your browser to: http://localhost:8000")
    print("2. Paste any GitHub repository URL")
    print("3. Choose your target platform")
    print("4. Click 'Convert to App'")
    print("\nThe application will:")
    print("- Clone the repository")
    print("- Parse the README for instructions")
    print("- Use AI to analyze the codebase")
    print("- Generate a working application")

if __name__ == "__main__":
    test_conversion()
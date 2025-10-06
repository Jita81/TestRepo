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
            print("⚠️  GitHub API rate limit exceeded or CSRF validation failed")
            print("   - If rate limit: Wait an hour or configure a GitHub token")
            print("   - If CSRF: Ensure CSRF token is properly included in request")
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   Details: {error_data['detail']}")
            except json.JSONDecodeError:
                print("   (Could not parse error details)")
        elif response.status_code == 422:
            print("❌ Invalid repository URL or request data")
            try:
                error_data = response.json()
                print(f"   Details: {error_data}")
            except json.JSONDecodeError:
                print("   (Could not parse error details)")
        elif response.status_code == 401:
            print("❌ Authentication required")
            print("   - Missing or invalid GitHub token")
            print("   - Check GITHUB_TOKEN in .env file")
        elif response.status_code == 404:
            print("❌ Repository not found")
            print("   - Repository may be private")
            print("   - URL may be incorrect")
            print("   - Repository may have been deleted")
        elif response.status_code == 429:
            print("⚠️  Rate limit exceeded")
            print("   - Too many requests to the server")
            print("   - Wait a few minutes and try again")
            try:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    print(f"   - Retry after: {retry_after} seconds")
            except:
                pass
        elif response.status_code == 500:
            print("❌ Server internal error")
            print("   - Check server logs for details")
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   Details: {error_data['detail']}")
            except json.JSONDecodeError:
                print("   (Could not parse error details)")
        elif response.status_code == 502 or response.status_code == 503:
            print("❌ Server temporarily unavailable")
            print("   - The server may be overloaded")
            print("   - Try again in a few minutes")
        else:
            print(f"❌ Conversion failed with status {response.status_code}")
            print(f"   Response: {response.text[:500]}")  # Limit response length
            
    except requests.exceptions.Timeout:
        print("⏰ Conversion timed out (this is normal for large repositories)")
        print("   - Try with a smaller repository")
        print("   - Increase timeout in configuration")
        print("   - Check network connection")
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL/TLS connection error: {e}")
        print("   - Check your internet connection")
        print("   - Verify SSL certificate configuration")
        print("   - Try updating your Python certificates: pip install --upgrade certifi")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Network connection error: {e}")
        print("   - Make sure the server is running and accessible")
        print("   - Check if port 8000 is open and not blocked by firewall")
        print("   - Verify the server URL is correct")
    except requests.exceptions.TooManyRedirects:
        print("❌ Too many redirects")
        print("   - There may be a configuration issue with the server")
        print("   - Contact the server administrator")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        print("   - Invalid response from server")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        print("   - General request failure")
        print("   - Check network connectivity")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response from server")
        print(f"   - Parse error at position {e.pos}")
        print(f"   - The server may have returned HTML instead of JSON")
    except KeyboardInterrupt:
        print("\n⚠️  Conversion interrupted by user")
        print("   - Press Ctrl+C again to exit")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        print("   - This is likely a bug")
        print("   - Please report this issue with the full error message")
    
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
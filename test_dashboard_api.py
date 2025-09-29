"""
Simple test script for Dashboard API endpoints
Run this to verify the dashboard API is working correctly.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_statistics_endpoint():
    """Test the statistics API endpoint."""
    print("\n📊 Testing Statistics Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/statistics")
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistics endpoint working!")
            print(f"   Total Conversions: {data['total_conversions']}")
            print(f"   Successful: {data['successful_conversions']}")
            print(f"   Failed: {data['failed_conversions']}")
            print(f"   Success Rate: {data['success_rate']}")
            return True
        else:
            print(f"❌ Statistics endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing statistics endpoint: {e}")
        return False

def test_recent_conversions_endpoint():
    """Test the recent conversions API endpoint."""
    print("\n📋 Testing Recent Conversions Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/recent-conversions")
        if response.status_code == 200:
            data = response.json()
            conversions = data.get('conversions', [])
            print(f"✅ Recent conversions endpoint working!")
            print(f"   Found {len(conversions)} conversions")
            for i, conv in enumerate(conversions[:3], 1):
                print(f"   {i}. {conv['repo_name']} - {conv['status']} ({conv['platform']})")
            return True
        else:
            print(f"❌ Recent conversions endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing recent conversions endpoint: {e}")
        return False

def test_populate_sample_data():
    """Test populating sample data."""
    print("\n🔄 Testing Populate Sample Data Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/populate-sample-data")
        if response.status_code == 200:
            data = response.json()
            print("✅ Sample data populated successfully!")
            print(f"   {data['message']}")
            return True
        else:
            print(f"❌ Populate sample data failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error populating sample data: {e}")
        return False

def test_dashboard_page():
    """Test if dashboard page loads."""
    print("\n🌐 Testing Dashboard Page...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully!")
            print(f"   Response length: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ Dashboard page failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing dashboard page: {e}")
        return False

def run_all_tests():
    """Run all dashboard tests."""
    print("="*60)
    print("🧪 Running Dashboard API Tests")
    print("="*60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test dashboard page
    results.append(("Dashboard Page", test_dashboard_page()))
    
    # Test populate sample data
    results.append(("Populate Sample Data", test_populate_sample_data()))
    
    # Test statistics after populating data
    results.append(("Statistics API", test_statistics_endpoint()))
    
    # Test recent conversions
    results.append(("Recent Conversions API", test_recent_conversions_endpoint()))
    
    # Print summary
    print("\n" + "="*60)
    print("📈 Test Summary")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTests Passed: {passed}/{total}")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is ready to use.")
        print(f"\n🌐 Visit the dashboard at: {BASE_URL}/dashboard")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    print("\n⚠️  Make sure the server is running before running these tests!")
    print("   Start the server with: python3 main.py\n")
    
    input("Press Enter to continue with tests... ")
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
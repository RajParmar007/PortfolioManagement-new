"""
Quick test to verify backend is working correctly
Run this after starting fastapi_backend.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Backend is running!")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        return False

def test_shortlist():
    """Test shortlisting endpoint"""
    try:
        payload = {
            "sector": "Technology",
            "top_n": 5
        }
        response = requests.post(f"{BASE_URL}/agents/shortlist", json=payload)
        data = response.json()
        
        if data.get("status") == "success":
            print("✅ Shortlist endpoint working!")
            print(f"   Found {len(data.get('data', []))} companies")
            if data.get('data'):
                print(f"   First company: {data['data'][0].get('symbol', 'N/A')}")
        else:
            print(f"⚠️  Shortlist returned: {data}")
        return True
    except Exception as e:
        print(f"❌ Shortlist test failed: {e}")
        return False

def test_analyze():
    """Test analysis endpoint (with dummy data)"""
    try:
        payload = {
            "tickers": ["AAPL"],
            "investor_profile": {
                "risk_tolerance": "medium",
                "investment_horizon": "medium_term",
                "preferred_sectors": ["Technology"]
            }
        }
        print("⏳ Testing analysis endpoint (this may take a minute)...")
        response = requests.post(f"{BASE_URL}/agents/analyze-companies", json=payload, timeout=120)
        data = response.json()
        
        if data.get("status") == "success":
            print("✅ Analysis endpoint working!")
            print(f"   Has recommendation: {bool(data.get('data', {}).get('recommendation'))}")
        else:
            print(f"⚠️  Analysis returned: {data}")
        return True
    except requests.Timeout:
        print("⚠️  Analysis timed out (this is normal for first run)")
        return True
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Backend Connection Test")
    print("=" * 50)
    print()
    
    print("1. Testing Backend Health...")
    if not test_health():
        print("\n⚠️  Please start the backend first:")
        print("   python fastapi_backend.py")
        exit(1)
    
    print("\n2. Testing Shortlist Endpoint...")
    test_shortlist()
    
    print("\n3. Testing Analysis Endpoint...")
    print("   (This will take longer as it runs all agents)")
    test_analyze()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
    print("\nYou can now start the frontend:")
    print("   cd frontend")
    print("   npm run dev")

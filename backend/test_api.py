#!/usr/bin/env python3
"""
Simple test script to verify the AI Startup Assistant API is working
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_api_docs():
    """Test that API documentation is accessible"""
    print("\n🔍 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API docs accessible at http://localhost:8000/docs")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing AI Startup Assistant API")
    print("=" * 50)
    
    test_health_check()
    test_api_docs()
    test_root_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 Next steps:")
    print("1. Set up your .env file with Supabase and OpenAI credentials")
    print("2. Visit http://localhost:8000/docs to explore the API")
    print("3. Test the /api/users/onboard endpoint with your credentials")

if __name__ == "__main__":
    main() 
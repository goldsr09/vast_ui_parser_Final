#!/usr/bin/env python3
"""
Test script to demonstrate broken wrapper detection functionality.
This script will test the VAST parser with URLs that might lead to empty VAST responses.
"""

import requests
import json
from parser_1 import parse_vast_and_store

def test_broken_wrapper_detection():
    """Test the broken wrapper detection functionality"""
    
    # Test URLs - you can replace these with actual VAST URLs that might have broken wrappers
    test_urls = [
        # Example URLs that might lead to empty VAST responses
        "https://example.com/vast1.xml",  # Replace with actual VAST URL
        "https://example.com/vast2.xml",  # Replace with actual VAST URL
    ]
    
    print("🧪 Testing Broken Wrapper Detection")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📡 Testing URL {i}: {url}")
        try:
            result = parse_vast_and_store(url, call_number=i)
            print(f"Result: {result}")
            
            # Check if broken wrapper was detected
            if "Broken wrapper detected" in result:
                print("✅ Broken wrapper detection working!")
            elif "No valid ads found" in result:
                print("⚠️ No ads found - might be a broken wrapper")
            else:
                print("✅ Ads found successfully")
                
        except Exception as e:
            print(f"❌ Error testing URL: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("\nTo view broken wrappers:")
    print("1. Start the Flask app: python app.py")
    print("2. Visit: http://localhost:5000/broken_wrappers")
    print("3. Or use the API: http://localhost:5000/api/broken_wrappers")

def test_api_endpoint():
    """Test the API endpoint for broken wrapper statistics"""
    try:
        response = requests.get("http://localhost:5000/api/broken_wrappers")
        if response.status_code == 200:
            data = response.json()
            print("\n📊 API Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ API request failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the Flask app is running.")

if __name__ == "__main__":
    print("🚀 VAST Broken Wrapper Detection Test")
    print("=" * 50)
    
    # Test the parser functionality
    test_broken_wrapper_detection()
    
    # Test the API endpoint (if app is running)
    print("\n🔗 Testing API endpoint...")
    test_api_endpoint()

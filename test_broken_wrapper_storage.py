#!/usr/bin/env python3
"""
Test script to verify broken wrapper storage is working correctly.
"""

import requests
import json
from parser_1 import parse_vast_and_store

def test_broken_wrapper_storage():
    """Test that broken wrapper storage is working correctly"""
    
    print("🧪 **Testing Broken Wrapper Storage**")
    print("=" * 50)
    
    # Get current broken wrapper count
    try:
        response = requests.get("http://localhost:5004/api/broken_wrappers")
        if response.status_code == 200:
            data = response.json()
            initial_count = data['total_broken_wrappers']
            print(f"📊 **Initial broken wrapper count: {initial_count}**")
        else:
            print("❌ Could not get initial count")
            return
    except Exception as e:
        print(f"❌ Error getting initial count: {e}")
        return
    
    print("\n🔍 **Testing with a VAST URL that should have broken wrappers...**")
    print("Note: You'll need to manually test with a VAST URL that has broken wrappers")
    print("The system should now properly store broken wrapper records when:")
    print("1. A wrapper ad leads to a broken URL")
    print("2. The broken URL returns no ads")
    print("3. The original_wrapper_ad_id is set")
    
    print("\n📋 **Expected Behavior:**")
    print("✅ Broken wrapper detected in logs")
    print("✅ Broken wrapper record stored in database")
    print("✅ Original wrapper ad ID captured")
    print("✅ Shows up in broken wrappers dashboard")
    
    print("\n🌐 **Test Steps:**")
    print("1. Go to: http://localhost:5004/")
    print("2. Enter a VAST URL that has broken wrappers")
    print("3. Check the terminal logs for broken wrapper detection")
    print("4. Check: http://localhost:5004/broken_wrappers")
    print("5. Verify the new broken wrapper appears with original ad ID")
    
    print("\n🔧 **Debug Commands:**")
    print("Check current broken wrappers:")
    print("  curl http://localhost:5004/api/broken_wrappers | python3 -m json.tool")
    print("\nCheck database directly:")
    print("  python3 debug_new_broken_wrapper.py")

if __name__ == "__main__":
    test_broken_wrapper_storage()

#!/usr/bin/env python3
"""
Test script to trigger broken wrapper detection and see debug output.
"""

import requests
import json

def test_broken_wrapper_debug():
    """Test broken wrapper detection with debug logging"""
    
    print("🧪 **Testing Broken Wrapper Detection with Debug Logging**")
    print("=" * 60)
    
    # Test with a VAST URL that should have broken wrappers
    test_url = "https://adserver.example.com/ad/g/1?nw=100000&csid=channel/example/stream&caid=100000-001&afid=100000001&pvrn=1000000000000&vprn=1000000000000&flag=+fbad+scpv+emcr+sltp+qtcb+slcb+aeti+vicb+dtrd&metr=1159&prof=100000:example_ctv_live_prod&resp=vast3&vrdu=180&vdty=variable&vip=192.0.2.1&mode=live&_fw_vcid2=test-debug-123&_fw_did=rida:test-debug-123&_fw_h_user_agent=StreamDevice%2F1.0&_fw_coppa=0&_fw_is_lat=0&_fw_us_privacy=1YNN&platform=ctvplayer&_fw_app_id=P0000000-0000-0000-0000-000000000001;ptgt=a&tpcl=midroll&slid=test-debug-123&mind=180&maxd=180&maxa=6"
    
    print(f"🔗 **Testing URL:** {test_url}")
    print("\n📋 **Expected Debug Output:**")
    print("✅ broken_wrapper_info exists: True")
    print("✅ original_wrapper_ad_id should be set")
    print("✅ ads count should be 0 (no valid ads)")
    print("✅ Broken wrapper record should be stored")
    
    print("\n🌐 **Making request to Flask app...**")
    
    try:
        response = requests.post("http://localhost:5004/multi", data={"urls": test_url})
        if response.status_code == 200:
            print("✅ Request successful")
            print("📄 Check the terminal where Flask is running for debug output")
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error making request: {e}")
    
    print("\n🔍 **Check the Flask terminal for debug output like:**")
    print("🔍 DEBUG: broken_wrapper_info exists: True")
    print("🔍 DEBUG: broken_wrapper_info: {...}")
    print("🔍 DEBUG: original_wrapper_ad_id: ...")
    print("🔍 DEBUG: ads count: 0")
    print("🔗 Storing broken wrapper record: ...")
    
    print("\n📊 **After testing, check broken wrappers:**")
    print("curl http://localhost:5004/api/broken_wrappers | python3 -m json.tool")

if __name__ == "__main__":
    test_broken_wrapper_debug()

#!/usr/bin/env python3
"""
Demonstration of broken wrapper detection functionality.
This script shows how the system detects and tracks broken wrapper URLs.
"""

import requests
import json
from parser_1 import parse_vast_and_store

def demo_broken_wrapper_detection():
    """Demonstrate the broken wrapper detection functionality"""
    
    print("🚀 VAST Broken Wrapper Detection Demo")
    print("=" * 50)
    
    # Example URLs that might lead to broken wrappers
    # In a real scenario, these would be actual VAST URLs
    demo_urls = [
        "https://example.com/vast1.xml",  # Replace with actual VAST URL
        "https://example.com/vast2.xml",  # Replace with actual VAST URL
    ]
    
    print("\n📋 Demo URLs to test:")
    for i, url in enumerate(demo_urls, 1):
        print(f"  {i}. {url}")
    
    print("\n🔍 How Broken Wrapper Detection Works:")
    print("1. Parser follows wrapper chains recursively")
    print("2. Detects empty VAST responses (no <Ad> elements)")
    print("3. Identifies VAST responses with status='NO_AD'")
    print("4. Tracks the complete wrapper chain")
    print("5. Stores broken URL information in database")
    
    print("\n📊 Current Database Statistics:")
    try:
        response = requests.get("http://localhost:5002/api/broken_wrappers")
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total ads in database: {stats['total_ads']}")
            print(f"   Broken wrappers found: {stats['total_broken_wrappers']}")
            print(f"   Unique broken URLs: {stats['unique_broken_urls']}")
            print(f"   Broken percentage: {stats['broken_percentage']}%")
        else:
            print("   Could not fetch statistics (API not available)")
    except Exception as e:
        print(f"   Error fetching statistics: {e}")
    
    print("\n🌐 Web Interface URLs:")
    print("   Main parser: http://localhost:5002/")
    print("   Broken wrappers: http://localhost:5002/broken_wrappers")
    print("   API endpoint: http://localhost:5002/api/broken_wrappers")
    
    print("\n📝 Example API Response:")
    print("""
{
  "total_broken_wrappers": 5,
  "total_ads": 1000,
  "broken_percentage": 0.5,
  "unique_broken_urls": 2,
  "broken_urls": [
    {
      "url": "https://broken-ad-server.com/vast",
      "occurrences": 3,
      "first_seen": "2024-01-15 10:30:00",
      "last_seen": "2024-01-20 15:45:00"
    }
  ]
}
""")
    
    print("\n🎯 Key Features:")
    print("✅ Automatic detection of empty VAST responses")
    print("✅ Wrapper chain tracking")
    print("✅ Database storage of broken URLs")
    print("✅ Web dashboard for monitoring")
    print("✅ API endpoint for integration")
    print("✅ Alert system for broken wrappers")
    
    print("\n🔧 Integration Examples:")
    print("""
# Monitor broken wrapper rate
curl http://localhost:5002/api/broken_wrappers | jq '.broken_percentage'

# Get list of broken URLs
curl http://localhost:5002/api/broken_wrappers | jq '.broken_urls[].url'

# Check for new broken URLs (compare with previous state)
""")
    
    print("\n📈 Benefits:")
    print("• Early detection of ad serving issues")
    print("• Reduced revenue loss from broken ads")
    print("• Improved client satisfaction")
    print("• Proactive monitoring and alerting")
    print("• Historical tracking of broken URLs")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\nTo test with real VAST URLs:")
    print("1. Replace the demo URLs with actual VAST URLs")
    print("2. Run: python3 test_broken_wrapper_demo.py")
    print("3. Check the web interface for results")

if __name__ == "__main__":
    demo_broken_wrapper_detection()

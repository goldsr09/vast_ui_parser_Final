#!/usr/bin/env python3
"""
Debug script to investigate why new broken wrapper detections aren't being stored.
"""

import sqlite3
import json

def debug_new_broken_wrapper():
    """Debug why new broken wrapper detections aren't being stored"""
    
    print("🔍 **Debugging New Broken Wrapper Storage**")
    print("=" * 50)
    
    conn = sqlite3.connect('vast_ads.db')
    cur = conn.cursor()
    
    # Check for any records created after the last known broken wrapper
    cur.execute('''
        SELECT id, ad_id, title, broken_wrapper_url, original_wrapper_ad_id, broken_wrapper_ad_id, 
               wrapped_ad, created_at
        FROM vast_ads 
        WHERE created_at > '2025-08-21 01:47:30'
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    recent_rows = cur.fetchall()
    
    print(f"\n📊 **Records Created After Last Known Broken Wrapper (2025-08-21 01:47:30):**")
    print(f"Found {len(recent_rows)} recent records")
    
    if recent_rows:
        for i, row in enumerate(recent_rows):
            print(f"\nRecent Record {i+1}:")
            print(f"  ID: {row[0]}")
            print(f"  Ad ID: {row[1]}")
            print(f"  Title: {row[2][:50] if row[2] else 'N/A'}...")
            print(f"  Broken URL: {row[3][:80] if row[3] else 'N/A'}...")
            print(f"  Original Wrapper Ad ID: {row[4] or 'N/A'}")
            print(f"  Broken Wrapper Ad ID: {row[5] or 'N/A'}")
            print(f"  Wrapped Ad: {'Yes' if row[6] else 'No'}")
            print(f"  Created: {row[7]}")
    else:
        print("❌ No recent records found after 2025-08-21 01:47:30")
    
    # Check for any broken wrapper records with the new ad ID from the logs
    cur.execute('''
        SELECT id, ad_id, title, broken_wrapper_url, original_wrapper_ad_id, broken_wrapper_ad_id, 
               wrapped_ad, created_at
        FROM vast_ads 
        WHERE ad_id LIKE '%12345678%' OR ad_id LIKE '%000000000000001%'
        ORDER BY created_at DESC
    ''')
    matching_rows = cur.fetchall()
    
    print(f"\n🔍 **Records Matching New Ad ID (12345678.000000000000001):**")
    print(f"Found {len(matching_rows)} matching records")
    
    if matching_rows:
        for i, row in enumerate(matching_rows):
            print(f"\nMatching Record {i+1}:")
            print(f"  ID: {row[0]}")
            print(f"  Ad ID: {row[1]}")
            print(f"  Title: {row[2][:50] if row[2] else 'N/A'}...")
            print(f"  Broken URL: {row[3][:80] if row[3] else 'N/A'}...")
            print(f"  Original Wrapper Ad ID: {row[4] or 'N/A'}")
            print(f"  Broken Wrapper Ad ID: {row[5] or 'N/A'}")
            print(f"  Wrapped Ad: {'Yes' if row[6] else 'No'}")
            print(f"  Created: {row[7]}")
    else:
        print("❌ No records found with the new ad ID")
    
    # Check total count of broken wrapper records
    cur.execute('''
        SELECT COUNT(*) 
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
    ''')
    total_broken = cur.fetchone()[0]
    
    print(f"\n📈 **Total Broken Wrapper Records: {total_broken}**")
    
    # Check if there are any records with broken_wrapper_url but no original_wrapper_ad_id
    cur.execute('''
        SELECT COUNT(*) 
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
        AND (original_wrapper_ad_id IS NULL OR original_wrapper_ad_id = '')
    ''')
    broken_without_original = cur.fetchone()[0]
    
    print(f"📈 **Broken Wrapper Records Without Original Ad ID: {broken_without_original}**")
    
    if broken_without_original > 0:
        print("⚠️ Found broken wrapper records without original ad IDs - these need updating")
        
        cur.execute('''
            SELECT id, ad_id, broken_wrapper_url, wrapped_ad, created_at
            FROM vast_ads 
            WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
            AND (original_wrapper_ad_id IS NULL OR original_wrapper_ad_id = '')
            ORDER BY created_at DESC
        ''')
        rows_to_update = cur.fetchall()
        
        print(f"\n📋 **Records That Need Updating:**")
        for i, row in enumerate(rows_to_update):
            print(f"  Record {i+1}: ID={row[0]}, Ad ID={row[1]}, Wrapped={row[3]}, Created={row[4]}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎯 **Analysis:**")
    if len(recent_rows) == 0:
        print("❌ No new records found - the parser may not be storing new broken wrappers")
        print("   This could indicate an issue with the storage logic")
    else:
        print("✅ New records found - checking if broken wrapper logic is working")
    
    if broken_without_original > 0:
        print(f"⚠️ {broken_without_original} broken wrapper records need original ad ID updates")

if __name__ == "__main__":
    debug_new_broken_wrapper()

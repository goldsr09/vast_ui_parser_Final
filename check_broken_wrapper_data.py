#!/usr/bin/env python3
"""
Script to check the current broken wrapper data in the database
and verify if the enhanced functionality is working correctly.
"""

import sqlite3
import json

def check_broken_wrapper_data():
    """Check the current broken wrapper data in the database"""
    
    print("🔍 **Checking Broken Wrapper Data**")
    print("=" * 50)
    
    conn = sqlite3.connect('vast_ads.db')
    cur = conn.cursor()
    
    # Check if the new columns exist
    cur.execute("PRAGMA table_info(vast_ads)")
    columns = [column[1] for column in cur.fetchall()]
    
    print("\n📋 **Database Schema Check:**")
    print(f"original_wrapper_ad_id column exists: {'original_wrapper_ad_id' in columns}")
    print(f"broken_wrapper_ad_id column exists: {'broken_wrapper_ad_id' in columns}")
    
    # Get all broken wrapper records
    cur.execute('''
        SELECT id, ad_id, title, broken_wrapper_url, original_wrapper_ad_id, broken_wrapper_ad_id, 
               wrapped_ad, created_at
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
        ORDER BY created_at DESC
    ''')
    rows = cur.fetchall()
    
    print(f"\n📊 **Total Broken Wrapper Records: {len(rows)}**")
    
    if rows:
        print("\n📋 **Recent Broken Wrapper Records:**")
        for i, row in enumerate(rows[:10]):  # Show last 10 records
            print(f"\nRecord {i+1}:")
            print(f"  ID: {row[0]}")
            print(f"  Ad ID: {row[1]}")
            print(f"  Title: {row[2][:50] if row[2] else 'N/A'}...")
            print(f"  Broken URL: {row[3][:80] if row[3] else 'N/A'}...")
            print(f"  Original Wrapper Ad ID: {row[4] or 'N/A'}")
            print(f"  Broken Wrapper Ad ID: {row[5] or 'N/A'}")
            print(f"  Wrapped Ad: {'Yes' if row[6] else 'No'}")
            print(f"  Created: {row[7]}")
    
    # Check for records with original_wrapper_ad_id
    cur.execute('''
        SELECT COUNT(*) 
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' 
        AND original_wrapper_ad_id IS NOT NULL AND original_wrapper_ad_id != ''
    ''')
    count_with_original_id = cur.fetchone()[0]
    
    print(f"\n📈 **Records with Original Wrapper Ad ID: {count_with_original_id}**")
    
    # Check for recent records (last hour)
    cur.execute('''
        SELECT COUNT(*) 
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' 
        AND created_at > datetime('now', '-1 hour')
    ''')
    recent_count = cur.fetchone()[0]
    
    print(f"📈 **Recent Broken Wrapper Records (last hour): {recent_count}**")
    
    # Show the most recent broken wrapper records
    if recent_count > 0:
        cur.execute('''
            SELECT id, ad_id, title, broken_wrapper_url, original_wrapper_ad_id, broken_wrapper_ad_id, 
                   wrapped_ad, created_at
            FROM vast_ads 
            WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
            AND created_at > datetime('now', '-1 hour')
            ORDER BY created_at DESC
        ''')
        recent_rows = cur.fetchall()
        
        print(f"\n🕐 **Recent Broken Wrapper Records (Last Hour):**")
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
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("🎯 **Analysis:**")
    if count_with_original_id == 0:
        print("❌ No records have original_wrapper_ad_id set")
        print("   This suggests the new functionality may not be working")
    else:
        print(f"✅ {count_with_original_id} records have original_wrapper_ad_id set")
        print("   The new functionality appears to be working")
    
    if recent_count == 0:
        print("❌ No recent broken wrapper records found")
        print("   Try parsing a new VAST URL to test the functionality")
    else:
        print(f"✅ {recent_count} recent broken wrapper records found")

if __name__ == "__main__":
    check_broken_wrapper_data()

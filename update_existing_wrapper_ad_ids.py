#!/usr/bin/env python3
"""
Script to update existing broken wrapper records with their original wrapper ad IDs.
This will populate the original_wrapper_ad_id and broken_wrapper_ad_id fields for existing records.
"""

import sqlite3
import json

def update_existing_wrapper_ad_ids():
    """Update existing broken wrapper records with original wrapper ad IDs"""
    
    print("🔧 **Updating Existing Broken Wrapper Records**")
    print("=" * 50)
    
    conn = sqlite3.connect('vast_ads.db')
    cur = conn.cursor()
    
    # Get all broken wrapper records that don't have original_wrapper_ad_id set
    cur.execute('''
        SELECT id, ad_id, broken_wrapper_url, wrapped_ad, ad_xml
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
        AND (original_wrapper_ad_id IS NULL OR original_wrapper_ad_id = '')
        ORDER BY created_at DESC
    ''')
    rows = cur.fetchall()
    
    print(f"📊 **Found {len(rows)} broken wrapper records to update**")
    
    if not rows:
        print("✅ No records need updating")
        conn.close()
        return
    
    updated_count = 0
    
    for row in rows:
        record_id, ad_id, broken_url, wrapped_ad, ad_xml = row
        
        print(f"\n🔍 **Processing Record ID {record_id}:**")
        print(f"  Ad ID: {ad_id}")
        print(f"  Wrapped Ad: {'Yes' if wrapped_ad else 'No'}")
        print(f"  Broken URL: {broken_url[:80]}...")
        
        # For wrapped ads, the ad_id IS the original wrapper ad ID
        if wrapped_ad:
            original_wrapper_ad_id = ad_id
            broken_wrapper_ad_id = ad_id
            print(f"  ✅ Setting original_wrapper_ad_id = {original_wrapper_ad_id}")
            print(f"  ✅ Setting broken_wrapper_ad_id = {broken_wrapper_ad_id}")
            
            # Update the record
            cur.execute('''
                UPDATE vast_ads 
                SET original_wrapper_ad_id = ?, broken_wrapper_ad_id = ?
                WHERE id = ?
            ''', (original_wrapper_ad_id, broken_wrapper_ad_id, record_id))
            
            updated_count += 1
        else:
            print(f"  ⚠️ Skipping - not a wrapped ad")
    
    # Commit the changes
    conn.commit()
    
    print(f"\n✅ **Updated {updated_count} records**")
    
    # Verify the updates
    cur.execute('''
        SELECT COUNT(*) 
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' 
        AND original_wrapper_ad_id IS NOT NULL AND original_wrapper_ad_id != ''
    ''')
    count_with_original_id = cur.fetchone()[0]
    
    print(f"📈 **Records with Original Wrapper Ad ID: {count_with_original_id}**")
    
    # Show updated records
    cur.execute('''
        SELECT id, ad_id, title, broken_wrapper_url, original_wrapper_ad_id, broken_wrapper_ad_id, 
               wrapped_ad, created_at
        FROM vast_ads 
        WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''
        AND original_wrapper_ad_id IS NOT NULL AND original_wrapper_ad_id != ''
        ORDER BY created_at DESC
    ''')
    updated_rows = cur.fetchall()
    
    print(f"\n📋 **Updated Records:**")
    for i, row in enumerate(updated_rows):
        print(f"\nRecord {i+1}:")
        print(f"  ID: {row[0]}")
        print(f"  Ad ID: {row[1]}")
        print(f"  Title: {row[2][:50] if row[2] else 'N/A'}...")
        print(f"  Broken URL: {row[3][:80] if row[3] else 'N/A'}...")
        print(f"  Original Wrapper Ad ID: {row[4]}")
        print(f"  Broken Wrapper Ad ID: {row[5]}")
        print(f"  Wrapped Ad: {'Yes' if row[6] else 'No'}")
        print(f"  Created: {row[7]}")
    
    conn.close()
    
    print("\n🎉 **Update Complete!**")
    print("Now the broken wrappers page and API will show the original wrapper ad IDs.")

if __name__ == "__main__":
    update_existing_wrapper_ad_ids()

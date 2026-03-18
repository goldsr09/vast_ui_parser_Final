#!/usr/bin/env python3
"""
Script to fix existing broken wrapper data in the database.
This removes incorrect broken wrapper markings from inline ads.
"""

import sqlite3
import json

def fix_existing_broken_wrapper_data():
    """Fix existing broken wrapper data by removing incorrect markings from inline ads"""
    
    print("🔧 **Fixing Existing Broken Wrapper Data**")
    print("=" * 50)
    
    conn = sqlite3.connect('vast_ads.db')
    cur = conn.cursor()
    
    # First, let's see what we have
    print("\n📊 **Current Data Analysis:**")
    
    # Count total ads with broken wrapper URLs
    cur.execute("SELECT COUNT(*) FROM vast_ads WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''")
    total_with_broken = cur.fetchone()[0]
    print(f"Total ads with broken_wrapper_url: {total_with_broken}")
    
    # Count wrapped ads with broken wrapper URLs
    cur.execute("SELECT COUNT(*) FROM vast_ads WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' AND wrapped_ad = 1")
    wrapped_with_broken = cur.fetchone()[0]
    print(f"Wrapped ads with broken_wrapper_url: {wrapped_with_broken}")
    
    # Count inline ads with broken wrapper URLs (these are the problem)
    cur.execute("SELECT COUNT(*) FROM vast_ads WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' AND wrapped_ad = 0")
    inline_with_broken = cur.fetchone()[0]
    print(f"Inline ads with broken_wrapper_url: {inline_with_broken}")
    
    if inline_with_broken > 0:
        print(f"\n❌ **Problem Found:** {inline_with_broken} inline ads incorrectly marked as broken wrappers")
        
        # Show some examples
        cur.execute("""
            SELECT id, ad_id, title, broken_wrapper_url 
            FROM vast_ads 
            WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' AND wrapped_ad = 0 
            LIMIT 5
        """)
        examples = cur.fetchall()
        
        print("\n📋 **Examples of Incorrectly Marked Inline Ads:**")
        for example in examples:
            print(f"  ID: {example[0]}, Ad ID: {example[1]}, Title: {example[2][:50]}...")
            print(f"    Broken URL: {example[3][:80]}...")
            print()
        
        # Fix the data
        print("🔧 **Fixing the data...**")
        
        # Remove broken wrapper info from inline ads
        cur.execute("""
            UPDATE vast_ads 
            SET broken_wrapper_url = NULL, wrapper_chain = NULL 
            WHERE wrapped_ad = 0 AND broken_wrapper_url IS NOT NULL
        """)
        
        fixed_count = cur.rowcount
        conn.commit()
        
        print(f"✅ **Fixed:** {fixed_count} inline ads had broken wrapper info removed")
        
        # Verify the fix
        cur.execute("SELECT COUNT(*) FROM vast_ads WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' AND wrapped_ad = 0")
        remaining_inline_with_broken = cur.fetchone()[0]
        print(f"Remaining inline ads with broken_wrapper_url: {remaining_inline_with_broken}")
        
        if remaining_inline_with_broken == 0:
            print("✅ **All inline ads fixed successfully!**")
        else:
            print(f"⚠️ **Warning:** {remaining_inline_with_broken} inline ads still have broken wrapper info")
    
    else:
        print("✅ **No inline ads incorrectly marked as broken wrappers found**")
    
    # Show final statistics
    print("\n📈 **Final Statistics:**")
    cur.execute("SELECT COUNT(*) FROM vast_ads WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != ''")
    final_total_with_broken = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM vast_ads WHERE broken_wrapper_url IS NOT NULL AND broken_wrapper_url != '' AND wrapped_ad = 1")
    final_wrapped_with_broken = cur.fetchone()[0]
    
    print(f"Total ads with broken_wrapper_url: {final_total_with_broken}")
    print(f"Wrapped ads with broken_wrapper_url: {final_wrapped_with_broken}")
    print(f"Inline ads with broken_wrapper_url: {final_total_with_broken - final_wrapped_with_broken}")
    
    conn.close()
    
    print("\n🎉 **Data Fix Complete!**")
    print("Now when you view ad details, inline ads should show their actual content")
    print("and only wrapper ads that truly led to broken URLs will be marked as broken.")

if __name__ == "__main__":
    fix_existing_broken_wrapper_data()

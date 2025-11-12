"""Import the latest session file with 3 trends."""

import json
import sqlite3
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

def import_new_session():
    json_file = "src/data/outputs/session_456/final_response_shri ranjani_20251106_210215.json"
    db_path = "src/data/trends.db"
    
    print(f"📁 Importing from: {json_file}")
    
    # Read JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    trends_data = data['response']['trends']
    session_id = data['metadata']['session_id']
    user_id = data['metadata']['user_id']
    timestamp = data['metadata']['timestamp']
    
    print(f"👤 Session: {session_id}")
    print(f"🧑 User: {user_id}")
    print(f"⏰ Timestamp: {timestamp}")
    
    # Show the trends we're trying to import
    makeup_trends = trends_data.get('makeupTrends', [])
    print(f"\n📊 Found {len(makeup_trends)} makeup trends:")
    for i, trend in enumerate(makeup_trends, 1):
        print(f"  {i}. {trend.get('trend_name', 'Unknown')}")
    
    # Check which ones already exist
    print(f"\n🔍 Checking for existing trends...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        existing_count = 0
        new_count = 0
        
        for trend in makeup_trends:
            trend_name = trend.get('trend_name', '')
            cursor.execute("SELECT COUNT(*) FROM trends WHERE LOWER(trend_name) = LOWER(?)", (trend_name,))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                print(f"  ⚠️  EXISTS: {trend_name}")
                existing_count += 1
            else:
                print(f"  ✅ NEW: {trend_name}")
                new_count += 1
        
        print(f"\n📊 Summary:")
        print(f"  - Existing trends: {existing_count}")
        print(f"  - New trends: {new_count}")
    
    # Now try to import using the database save method
    print(f"\n🔄 Testing database save with duplicate prevention...")
    
    try:
        # Import the database module
        from src.utils.database import db
        
        # Test the save_trends_batch method
        result = db.save_trends_batch(trends_data, session_id)
        print(f"✅ Save result: {result} new trends added")
        
    except Exception as e:
        print(f"❌ Error during database save: {e}")
    
    # Check final database state
    print(f"\n📊 Final database check...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trends")
        total_trends = cursor.fetchone()[0]
        print(f"Total trends in database: {total_trends}")

if __name__ == "__main__":
    print("New Session Import Test")
    print("=" * 30)
    import_new_session()
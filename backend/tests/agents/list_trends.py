"""List recent trends from database."""

import sqlite3
import os

db_path = "src/data/trends.db"

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    
    # Get the most recent trends
    cursor.execute("""
        SELECT trend_name, category, created_at 
        FROM trends 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    trends = cursor.fetchall()
    
    print("Recent Trends in Database:")
    print("=" * 40)
    for i, (name, category, created) in enumerate(trends, 1):
        print(f"{i:2d}. {name} ({category})")
        print(f"    Created: {created}")
        print()
    
    # Check specifically for our new trends
    new_trends = ["Strawberry Girl Makeup", "Honey Lips", "Espresso Makeup"]
    
    print("Checking for specific trends:")
    print("=" * 40)
    for trend_name in new_trends:
        cursor.execute("SELECT COUNT(*) FROM trends WHERE trend_name = ?", (trend_name,))
        count = cursor.fetchone()[0]
        status = "✅ EXISTS" if count > 0 else "❌ NOT FOUND"
        print(f"{trend_name}: {status}")
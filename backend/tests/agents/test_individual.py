"""Test individual trend saves."""

import json
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.utils.database import db

# Read the JSON file
with open('src/data/outputs/session_456/final_response_shri ranjani_20251106_210215.json', 'r') as f:
    data = json.load(f)

trends_data = data['response']['trends']
session_id = data['metadata']['session_id']

print('Testing individual trend saves:')
print('=' * 40)

for trend in trends_data['makeupTrends']:
    trend_name = trend['trend_name']
    print(f"\nTesting: {trend_name}")
    
    # Check if it exists first
    exists = db.check_trend_exists(trend_name)
    print(f"Already exists: {exists}")
    
    # Try to save it
    result = db.save_trend(trend, session_id, 'Makeup')
    print(f"Save result: {result}")
    
print('\n' + '=' * 40)
print('Test complete!')
"""Script to insert trends from JSON file into my_trends.csv, avoiding duplicates."""

import os
import json
import csv
import sys
from datetime import datetime
from typing import Dict, List, Set

# Add the backend directory to the path so we can import from src
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from src.utils.setup_log import setup_logger

# Setup logger
logger = setup_logger()

def load_existing_trends(csv_path: str) -> Set[str]:
    """Load existing trend names from CSV file to avoid duplicates."""
    existing_trends = set()
    
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    trend_name = row.get('trend_name', '').strip()
                    if trend_name:
                        existing_trends.add(trend_name.lower())  # Use lowercase for comparison
                        
            logger.info(f"Loaded {len(existing_trends)} existing trends from CSV")
        except Exception as e:
            logger.error(f"Error reading existing CSV: {e}")
    else:
        logger.info("No existing CSV file found - will create new one")
    
    return existing_trends

def extract_trends_from_json(json_path: str) -> List[Dict]:
    """Extract all trends from the JSON file."""
    trends_list = []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded JSON file: {json_path}")
        
        # Extract trends data
        if 'response' in data and 'trends' in data['response']:
            trends_data = data['response']['trends']
            session_id = data['metadata']['session_id']
            user_id = data['metadata']['user_id']
            
            # Category mapping
            category_mapping = {
                'makeupTrends': 'Makeup',
                'makeup_trends': 'Makeup',
                'skincareTrends': 'Skincare', 
                'skincare_trends': 'Skincare',
                'hairTrends': 'Hair',
                'hair_trends': 'Hair',
                'toolsBrushesTrends': 'Tools & Brushes',
                'tools_brushes_trends': 'Tools & Brushes',
                'miniSizeTrends': 'Mini Size',
                'mini_size_trends': 'Mini Size',
                'menTrends': 'Men',
                'men_trends': 'Men',
                'giftsTrends': 'Gifts',
                'gifts_trends': 'Gifts',
                'fragranceTrends': 'Fragrance',
                'fragrance_trends': 'Fragrance',
                'bathBodyTrends': 'Bath & Body',
                'bath_body_trends': 'Bath & Body'
            }
            
            # Process each category
            for category_key, trends_list_data in trends_data.items():
                if isinstance(trends_list_data, list):
                    category_name = category_mapping.get(category_key, category_key.replace('_', ' ').title())
                    
                    for trend in trends_list_data:
                        # Create standardized trend record
                        trend_record = {
                            'trend_id': trend.get('id', ''),
                            'trend_name': trend.get('trend_name', ''),
                            'trend_description': trend.get('trend_description', ''),
                            'trend_summary': trend.get('trend_summary', ''),
                            'category': category_name,
                            'keywords': ', '.join(trend.get('keywords', [])) if isinstance(trend.get('keywords'), list) else str(trend.get('keywords', '')),
                            'hashtags': ', '.join(trend.get('hashtags', [])) if isinstance(trend.get('hashtags'), list) else str(trend.get('hashtags', ''))
                        }
                        trends_list.append(trend_record)
                        
            logger.info(f"Extracted {len(trends_list)} trends from JSON")
            
            # Log category breakdown
            category_counts = {}
            for trend in trends_list:
                category = trend['category']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            for category, count in category_counts.items():
                logger.info(f"   └─ {category}: {count} trends")
                
        else:
            logger.error("No trends data found in JSON file")
            
    except Exception as e:
        logger.error(f"Error extracting trends from JSON: {e}")
        
    return trends_list

def insert_new_trends_to_csv(trends_list: List[Dict], existing_trends: Set[str], csv_path: str) -> int:
    """Insert new trends to CSV file, skipping duplicates."""
    new_trends_count = 0
    skipped_count = 0
    
    # Determine if we need to write headers (new file)
    file_exists = os.path.exists(csv_path)
    
    try:
        # Filter out existing trends
        new_trends = []
        for trend in trends_list:
            trend_name = trend['trend_name'].strip()
            if trend_name.lower() not in existing_trends:
                new_trends.append(trend)
                new_trends_count += 1
            else:
                skipped_count += 1
                logger.info(f"Skipping existing trend: '{trend_name}'")
        
        if new_trends:
            # Write to CSV file
            with open(csv_path, 'a', encoding='utf-8', newline='') as csvfile:
                fieldnames = [
                    'trend_id', 'trend_name', 'trend_description', 'trend_summary', 'category', 'keywords', 'hashtags'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    logger.info("Created new CSV file with headers")
                # Write new trends
                writer.writerows(new_trends)
                logger.info(f"Added {new_trends_count} new trends to CSV")
        else:
            logger.info("No new trends to add - all trends already exist")
        logger.info(f"Summary: {new_trends_count} added, {skipped_count} skipped")
    except Exception as e:
        logger.error(f"Error writing to CSV: {e}")
    return new_trends_count

def main():
    """Main function to process JSON and update my_trends.csv."""
    
    logger.info("=" * 60)
    logger.info("INSERTING TRENDS TO MY_TRENDS.CSV")
    logger.info("=" * 60)
    
    # Accept JSON file path as a command-line argument
    import sys
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        logger.info(f"Using JSON file from argument: {json_path}")
    else:
        json_path = "src/data/outputs/session_789/final_response_shri ranjani_20251106_225212.json"
        logger.info(f"Using default JSON file: {json_path}")

    csv_path = "src/data/exports/my_trends.csv"

    # Ensure the exports directory exists
    exports_dir = os.path.dirname(csv_path)
    os.makedirs(exports_dir, exist_ok=True)

    # Check if JSON file exists
    if not os.path.exists(json_path):
        logger.error(f"JSON file not found: {json_path}")
        return

    logger.info(f"Source JSON: {json_path}")
    logger.info(f"Target CSV: {csv_path}")

    # Load existing trends
    existing_trends = load_existing_trends(csv_path)

    # Extract trends from JSON
    trends_list = extract_trends_from_json(json_path)

    if not trends_list:
        logger.error("No trends extracted from JSON file")
        return

    # Insert new trends to CSV
    added_count = insert_new_trends_to_csv(trends_list, existing_trends, csv_path)

    logger.info("=" * 60)
    logger.info("PROCESS COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Total trends processed: {len(trends_list)}")
    logger.info(f"New trends added: {added_count}")
    logger.info(f"File location: {os.path.abspath(csv_path)}")

if __name__ == "__main__":
    print("Inserting trends from JSON to my_trends.csv...")
    print("Check src/logs/app_logs.log for detailed processing logs")
    main()
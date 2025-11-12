"""Utility functions for saving agent outputs to files and CSV/Excel exports."""

import os
import sys
import json
import csv
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List
from src.utils.setup_log import setup_logger

logger = setup_logger()


def export_trends_to_csv_excel(
    trends_data: Dict,
    session_id: str,
    user_id: str,
    session_dir: str
) -> tuple[str, str]:
    """
    Export trends data to both CSV and Excel formats.
    
    Args:
        trends_data: Dictionary containing trends by category
        session_id: Session identifier
        user_id: User identifier
        session_dir: Directory to save exports in
    
    Returns:
        tuple: (csv_filepath, excel_filepath)
    """
    try:
        # Prepare data for export
        export_rows = []
        
        # Extract trends from all categories
        for category_key, trends_list in trends_data.items():
            if isinstance(trends_list, list):
                # Map category key to readable name
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
                
                category_name = category_mapping.get(category_key, category_key.replace('_', ' ').title())
                
                for trend in trends_list:
                    # Extract and flatten trend data
                    row = {
                        'trend_id': trend.get('id', ''),
                        'trend_name': trend.get('trend_name', ''),
                        'category': category_name,
                        'trend_description': trend.get('trend_description', ''),
                        'trend_summary': trend.get('trend_summary', ''),
                        'keywords': ', '.join(trend.get('keywords', [])) if isinstance(trend.get('keywords'), list) else str(trend.get('keywords', '')),
                        'hashtags': ', '.join(trend.get('hashtags', [])) if isinstance(trend.get('hashtags'), list) else str(trend.get('hashtags', '')),
                        'virality_score': trend.get('virality', ''),
                        'consumer_sentiment': trend.get('consumer_sentiment', ''),
                        'difficulty_level': trend.get('difficulty_level', ''),
                        'target_demographic': trend.get('target_demographic', ''),
                        'popularity_score': trend.get('popularity_score', ''),
                        'social_media_mentions': trend.get('social_media_mentions', ''),
                        'key_products': ', '.join(trend.get('key_products', [])) if isinstance(trend.get('key_products'), list) else str(trend.get('key_products', '')),
                        'techniques': ', '.join(trend.get('techniques', [])) if isinstance(trend.get('techniques'), list) else str(trend.get('techniques', '')),
                        'sources': ', '.join(trend.get('sources', [])) if isinstance(trend.get('sources'), list) else str(trend.get('sources', '')),
                        'image_urls': ', '.join(trend.get('image_urls', [])) if isinstance(trend.get('image_urls'), list) else str(trend.get('image_urls', '')),
                        'session_id': session_id,
                        'export_date': datetime.utcnow().strftime("%Y-%m-%d"),
                        'export_time': datetime.utcnow().strftime("%H:%M:%S")
                    }
                    export_rows.append(row)
        
        if not export_rows:
            logger.warning("No trends data found for export")
            return "", ""
        
        # Create timestamp for file naming
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Export to CSV
        csv_filename = f"trends_export_{user_id}_{timestamp}.csv"
        csv_filepath = os.path.join(session_dir, csv_filename)
        
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = export_rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(export_rows)
        
        # Export to Excel
        excel_filename = f"trends_export_{user_id}_{timestamp}.xlsx"
        excel_filepath = os.path.join(session_dir, excel_filename)
        
        df = pd.DataFrame(export_rows)
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            # Write all trends to main sheet
            df.to_excel(writer, sheet_name='All_Trends', index=False)
            
            # Create separate sheets for each category
            for category in df['category'].unique():
                category_df = df[df['category'] == category]
                sheet_name = category.replace(' & ', '_').replace(' ', '_')[:31]  # Excel sheet name limit
                category_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"=== TRENDS EXPORT COMPLETE ===")
        logger.info(f"CSV file: {csv_filepath}")
        logger.info(f"Excel file: {excel_filepath}")
        logger.info(f"Total trends exported: {len(export_rows)}")
        logger.info(f"Categories: {len(df['category'].unique())}")
        
        return csv_filepath, excel_filepath
        
    except Exception as e:
        logger.error(f"Failed to export trends to CSV/Excel: {e}")
        return "", ""

def save_agent_output(
    agent_name: str, 
    output_data: Any, 
    session_id: str, 
    user_id: str,
    output_dir: str = "src/data/outputs"
) -> str:
    """
    Save agent output to a file in the outputs directory organized by session.
    
    Args:
        agent_name: Name of the agent (e.g., 'trend_research_agent')
        output_data: The data to save (will be JSON serialized)
        session_id: Session identifier
        user_id: User identifier
        output_dir: Directory to save files in
    
    Returns:
        str: Path to the saved file
    """
    try:
        # Ensure output directory exists with session subdirectory
        abs_output_dir = os.path.abspath(output_dir)
        session_dir = os.path.join(abs_output_dir, f"session_{session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Create timestamp for file naming
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create filename with agent and timestamp (no need for session in filename since it's in folder)
        filename = f"{agent_name}_{user_id}_{timestamp}.json"
        filepath = os.path.join(session_dir, filename)
        
        # Prepare data structure with metadata
        file_data = {
            "metadata": {
                "agent_name": agent_name,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "saved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            },
            "output": output_data
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"=== AGENT OUTPUT SAVED ===")
        logger.info(f"Agent: {agent_name}")
        logger.info(f"Session folder: {session_dir}")
        logger.info(f"File: {filepath}")
        logger.info(f"Data type: {type(output_data)}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to save agent output for {agent_name}: {e}")
        return ""


def save_session_state(
    session_state: Dict[str, Any], 
    session_id: str, 
    user_id: str,
    output_dir: str = "src/data/outputs"
) -> str:
    """
    Save complete session state to a file organized by session.
    
    Args:
        session_state: Complete session state dictionary
        session_id: Session identifier
        user_id: User identifier
        output_dir: Directory to save files in
    
    Returns:
        str: Path to the saved file
    """
    try:
        # Ensure output directory exists with session subdirectory
        abs_output_dir = os.path.abspath(output_dir)
        session_dir = os.path.join(abs_output_dir, f"session_{session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Create timestamp for file naming
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create filename for session state
        filename = f"session_state_{user_id}_{timestamp}.json"
        filepath = os.path.join(session_dir, filename)
        
        # Prepare data structure with metadata
        file_data = {
            "metadata": {
                "type": "session_state",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "saved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "session_keys": list(session_state.keys()) if session_state else []
            },
            "session_state": session_state
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"=== SESSION STATE SAVED ===")
        logger.info(f"Session folder: {session_dir}")
        logger.info(f"File: {filepath}")
        logger.info(f"Session keys: {list(session_state.keys()) if session_state else 'None'}")
        
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to save session state: {e}")
        return ""


def save_final_response(
    response_data: Any, 
    session_id: str, 
    user_id: str,
    query: str = "",
    output_dir: str = "src/data/outputs"
) -> str:
    """
    Save final API response to a file and database organized by session.
    
    Args:
        response_data: Final response data to save
        session_id: Session identifier
        user_id: User identifier
        query: Original user query
        output_dir: Directory to save files in
    
    Returns:
        str: Path to the saved file
    """
    try:
        # Ensure output directory exists with session subdirectory
        abs_output_dir = os.path.abspath(output_dir)
        session_dir = os.path.join(abs_output_dir, f"session_{session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        # Create timestamp for file naming
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create filename for final response
        filename = f"final_response_{user_id}_{timestamp}.json"
        filepath = os.path.join(session_dir, filename)
        
        # Prepare data structure with metadata
        file_data = {
            "metadata": {
                "type": "final_response",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "saved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "response_type": type(response_data).__name__
            },
            "response": response_data
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Export to CSV/Excel if response_data contains trends
        if isinstance(response_data, dict) and 'trends' in response_data:
            trends_data = response_data['trends']
            
            # Export trends to CSV and Excel
            csv_path, excel_path = export_trends_to_csv_excel(
                trends_data=trends_data,
                session_id=session_id,
                user_id=user_id,
                session_dir=session_dir
            )
            
            if csv_path and excel_path:
                logger.info(f"=== TRENDS EXPORT COMPLETE ===")
                logger.info(f"CSV exported to: {csv_path}")
                logger.info(f"Excel exported to: {excel_path}")
            else:
                logger.warning("Failed to export trends to CSV/Excel")
        
        logger.info(f"=== FINAL RESPONSE SAVED ===")
        logger.info(f"Session folder: {session_dir}")
        logger.info(f"File: {filepath}")
        logger.info(f"Response type: {type(response_data)}")
        
        # After saving the JSON, trigger the insert_trends_to_csv pipeline with the actual JSON file path
        try:
            import subprocess
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'insert_trends_to_csv.py'))
            # Pass the just-created JSON file as an argument (filepath is the full path to the JSON file just written)
            subprocess.Popen([
                sys.executable, script_path, filepath
            ])
            logger.info(f"Triggered insert_trends_to_csv.py for {filepath}")
        except Exception as e:
            logger.error(f"Failed to trigger insert_trends_to_csv.py: {e}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save final response: {e}")
        return ""


def create_session_summary(
    session_id: str, 
    user_id: str, 
    query: str,
    output_dir: str = "src/data/outputs"
) -> str:
    """
    Create a summary file for the session with metadata and file listing.
    
    Args:
        session_id: Session identifier
        user_id: User identifier
        query: Original user query
        output_dir: Directory where files are saved
    
    Returns:
        str: Path to the summary file
    """
    try:
        # Ensure session directory exists
        abs_output_dir = os.path.abspath(output_dir)
        session_dir = os.path.join(abs_output_dir, f"session_{session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        # List all files in the session directory
        session_files = []
        if os.path.exists(session_dir):
            for file in os.listdir(session_dir):
                if file.endswith('.json') and file != 'session_summary.json':
                    filepath = os.path.join(session_dir, file)
                    file_info = {
                        "filename": file,
                        "size_bytes": os.path.getsize(filepath),
                        "created": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                    }
                    session_files.append(file_info)
        
        # Create summary data
        summary_data = {
            "session_metadata": {
                "session_id": session_id,
                "user_id": user_id,
                "original_query": query,
                "session_start": datetime.utcnow().isoformat(),
                "summary_created": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "total_files": len(session_files)
            },
            "files_created": session_files,
            "session_structure": {
                "trend_research_outputs": [f for f in session_files if "trend_research_agent" in f["filename"]],
                "output_composer_outputs": [f for f in session_files if "output_composer_agent" in f["filename"]],
                "session_states": [f for f in session_files if "session_state" in f["filename"]],
                "final_responses": [f for f in session_files if "final_response" in f["filename"]]
            }
        }
        
        # Save summary file
        summary_filepath = os.path.join(session_dir, "session_summary.json")
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"=== SESSION SUMMARY CREATED ===")
        logger.info(f"Session: {session_id}")
        logger.info(f"Summary file: {summary_filepath}")
        logger.info(f"Total files: {len(session_files)}")
        
        return summary_filepath
        
    except Exception as e:
        logger.error(f"Failed to create session summary: {e}")
        return ""
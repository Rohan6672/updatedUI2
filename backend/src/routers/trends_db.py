"""Router for database trend queries and statistics."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from src.utils.database import db
from src.utils.setup_log import setup_logger

logger = setup_logger()

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("/session/{session_id}")
async def get_session_trends(session_id: str):
    """Get all trends for a specific session."""
    try:
        logger.info(f"Fetching trends for session: {session_id}")
        trends = db.get_session_trends(session_id)
        
        if not trends:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No trends found for session {session_id}"
            )
        
        logger.info(f"Found {len(trends)} trends for session {session_id}")
        return {
            "session_id": session_id,
            "total_trends": len(trends),
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error fetching session trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trends: {str(e)}"
        )

@router.get("/recent")
async def get_recent_trends(limit: int = Query(50, ge=1, le=200)):
    """Get recent trends across all sessions."""
    try:
        logger.info(f"Fetching {limit} recent trends")
        trends = db.get_recent_trends(limit)
        
        logger.info(f"Found {len(trends)} recent trends")
        return {
            "total_trends": len(trends),
            "limit": limit,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trends: {str(e)}"
        )

@router.get("/category/{category}")
async def get_trends_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get trends by category."""
    try:
        logger.info(f"Fetching {limit} trends for category: {category}")
        trends = db.get_trends_by_category(category, limit)
        
        if not trends:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No trends found for category {category}"
            )
        
        logger.info(f"Found {len(trends)} trends for category {category}")
        return {
            "category": category,
            "total_trends": len(trends),
            "limit": limit,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error fetching category trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching trends: {str(e)}"
        )

@router.get("/search")
async def search_trends(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search trends by name or description."""
    try:
        logger.info(f"Searching trends with query: '{q}', category: {category}, limit: {limit}")
        
        # Since we don't have a full-text search in basic SQLite, we'll use a simple LIKE query
        import sqlite3
        
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query based on filters
            if category:
                cursor.execute("""
                    SELECT t.*, s.user_id 
                    FROM trends t
                    JOIN sessions s ON t.session_id = s.session_id
                    WHERE (t.trend_name LIKE ? OR t.trend_description LIKE ? OR t.trend_summary LIKE ?)
                    AND t.category = ?
                    ORDER BY t.created_at DESC
                    LIMIT ?
                """, (f"%{q}%", f"%{q}%", f"%{q}%", category, limit))
            else:
                cursor.execute("""
                    SELECT t.*, s.user_id 
                    FROM trends t
                    JOIN sessions s ON t.session_id = s.session_id
                    WHERE t.trend_name LIKE ? OR t.trend_description LIKE ? OR t.trend_summary LIKE ?
                    ORDER BY t.created_at DESC
                    LIMIT ?
                """, (f"%{q}%", f"%{q}%", f"%{q}%", limit))
            
            trends = [dict(row) for row in cursor.fetchall()]
        
        logger.info(f"Found {len(trends)} trends matching search")
        return {
            "query": q,
            "category": category,
            "total_results": len(trends),
            "limit": limit,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error searching trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching trends: {str(e)}"
        )

@router.get("/stats")
async def get_database_stats():
    """Get database statistics."""
    try:
        logger.info("Fetching database statistics")
        stats = db.get_database_stats()
        
        logger.info(f"Database stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )

@router.get("/categories")
async def get_available_categories():
    """Get list of all available categories."""
    try:
        logger.info("Fetching available categories")
        
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, COUNT(*) as trend_count
                FROM trends
                GROUP BY category
                ORDER BY trend_count DESC
            """)
            
            categories = [{"category": row[0], "trend_count": row[1]} for row in cursor.fetchall()]
        
        logger.info(f"Found {len(categories)} categories")
        return {
            "total_categories": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def delete_session_trends(session_id: str):
    """Delete all trends and session data for a specific session."""
    try:
        logger.info(f"Deleting session data for: {session_id}")
        
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete trend details first (foreign key constraint)
            cursor.execute("""
                DELETE FROM trend_details 
                WHERE trend_id IN (
                    SELECT id FROM trends WHERE session_id = ?
                )
            """, (session_id,))
            
            # Delete trends
            cursor.execute("DELETE FROM trends WHERE session_id = ?", (session_id,))
            trends_deleted = cursor.rowcount
            
            # Delete session categories
            cursor.execute("DELETE FROM session_categories WHERE session_id = ?", (session_id,))
            
            # Delete session
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            session_deleted = cursor.rowcount
            
            conn.commit()
        
        if session_deleted == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        logger.info(f"Deleted {trends_deleted} trends for session {session_id}")
        return {
            "session_id": session_id,
            "trends_deleted": trends_deleted,
            "message": "Session data deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )
"""Query history API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.api.deps import get_current_user
from app.models.schemas import (
    QueryLog, SavedQuery, BookmarkRequest,
    HistoryResponse, UserInDB, QueryType
)


router = APIRouter()


# Demo history storage (in production, use database)
_demo_history = []


@router.get("", response_model=HistoryResponse)
async def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    query_type: Optional[QueryType] = Query(None, description="Filter by query type"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get query history for the current user.
    
    Returns paginated list of past queries with responses.
    """
    # Demo: Return sample history
    from datetime import datetime, timedelta
    
    demo_items = [
        QueryLog(
            id=f"query-{i}",
            user_id=current_user.id,
            query_text=f"Sample query {i}",
            response_text=f"Sample response for query {i}",
            sources=[],
            query_type=QueryType.CHAT,
            response_time_ms=150 + i * 10,
            created_at=datetime.utcnow() - timedelta(hours=i)
        )
        for i in range(1, 6)
    ]
    
    return HistoryResponse(
        items=demo_items,
        total=len(demo_items),
        page=page,
        page_size=page_size,
        has_more=False
    )


@router.get("/{query_id}", response_model=QueryLog)
async def get_query(
    query_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific query from history.
    """
    from datetime import datetime
    
    # Demo response
    return QueryLog(
        id=query_id,
        user_id=current_user.id,
        query_text="What are the first-line treatments for hypertension?",
        response_text="First-line treatments for hypertension include...",
        sources=[],
        query_type=QueryType.CHAT,
        response_time_ms=250,
        created_at=datetime.utcnow()
    )


@router.post("/{query_id}/bookmark", response_model=SavedQuery)
async def bookmark_query(
    query_id: str,
    request: BookmarkRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Bookmark a query for future reference.
    """
    from datetime import datetime
    
    # Demo: Create saved query
    query = QueryLog(
        id=query_id,
        user_id=current_user.id,
        query_text="Bookmarked query",
        response_text="Response text",
        sources=[],
        query_type=QueryType.CHAT,
        response_time_ms=200,
        created_at=datetime.utcnow()
    )
    
    return SavedQuery(
        id=f"saved-{query_id}",
        query_log_id=query_id,
        title=request.title,
        notes=request.notes,
        query=query,
        created_at=datetime.utcnow()
    )


@router.delete("/{query_id}/bookmark")
async def unbookmark_query(
    query_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Remove bookmark from a query.
    """
    return {"message": "Bookmark removed", "query_id": query_id}


@router.delete("/{query_id}")
async def delete_query(
    query_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a query from history.
    
    Note: In a production system with audit requirements,
    you might soft-delete instead of hard-delete.
    """
    return {"message": "Query deleted", "query_id": query_id}


@router.get("/bookmarks/all", response_model=list[SavedQuery])
async def get_bookmarks(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all bookmarked queries for the current user.
    """
    from datetime import datetime
    
    # Demo: Return empty list or sample bookmarks
    return []


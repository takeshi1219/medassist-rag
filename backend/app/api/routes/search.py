"""Search API routes - Direct vector search."""
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.api.deps import get_current_user_optional
from app.models.schemas import (
    SearchRequest, SearchResponse, SearchResult, UserInDB
)
from app.core.rag.retriever import get_retriever


router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    current_user: UserInDB = Depends(get_current_user_optional)
):
    """
    Direct search of the medical knowledge base.
    
    Returns raw search results without LLM-generated answers.
    Useful for browsing the source material directly.
    """
    try:
        logger.info(f"Search request: {request.query[:50]}...")
        
        retriever = get_retriever()
        sources = await retriever.retrieve(
            query=request.query,
            k=request.limit,
            filters=request.filters if request.filters else None
        )
        
        results = [
            SearchResult(
                id=str(i),
                content=source.content,
                title=source.metadata.get("title"),
                source_type=source.metadata.get("source_type", "unknown"),
                metadata=source.metadata,
                score=source.score
            )
            for i, source in enumerate(sources)
        ]
        
        return SearchResponse(
            results=results,
            total=len(results),
            query=request.query,
            search_type=request.search_type
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching"
        )


@router.get("")
async def search_get(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    source_type: str = Query(None, description="Filter by source type")
):
    """
    Direct search (GET version for simple queries).
    """
    filters = {}
    if source_type:
        filters["source_type"] = source_type
    
    request = SearchRequest(
        query=q,
        limit=limit,
        filters=filters
    )
    
    return await search(request, None)


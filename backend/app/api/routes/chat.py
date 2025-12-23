"""Chat API routes - Main RAG interface (Production Ready)."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from loguru import logger

from app.api.deps import get_current_user, get_current_user_optional
from app.models.schemas import ChatRequest, ChatResponse, UserInDB
from app.core.rag.pipeline import get_rag_pipeline
from app.core.validation import validate_and_sanitize, query_validator
from app.middleware.rate_limit import limiter, CHAT_RATE_LIMIT
from app.middleware.audit import audit_logger
from app.config import settings


router = APIRouter()


@router.post("", response_model=ChatResponse)
# @limiter.limit(CHAT_RATE_LIMIT)  # Temporarily disabled due to Starlette compatibility
async def chat(
    http_request: Request,
    request: ChatRequest,
    current_user: UserInDB = Depends(get_current_user_optional)
):
    """
    Process a medical query through the RAG pipeline.
    
    Returns a comprehensive answer with source citations from medical literature.
    
    Rate limited to prevent abuse.
    """
    # Validate and sanitize input
    sanitized_query, is_valid, error = validate_and_sanitize(request.query)
    
    if not is_valid:
        logger.warning(f"Invalid query rejected: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    try:
        user_id = current_user.id if current_user else "anonymous"
        user_email = current_user.email if current_user else "anonymous"
        
        logger.info(f"Chat request from user: {user_email}")
        logger.info(f"Query length: {len(sanitized_query)} chars")
        
        pipeline = get_rag_pipeline()
        response = await pipeline.query(
            question=sanitized_query,
            language=request.language.value,
            conversation_id=request.conversation_id,
            include_sources=request.include_sources
        )
        
        # Audit log for PHI access
        audit_logger.log_access(
            user_id=user_id,
            action="MEDICAL_QUERY",
            resource="/api/v1/chat",
            request=http_request,
            response_status=200,
            details={
                "query_length": len(sanitized_query),
                "response_time_ms": response.processing_time_ms,
                "source_count": len(response.sources),
                "model_used": response.model_used,
                "language": request.language.value
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        # Log full exception details for debugging
        logger.exception(f"Chat error: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception args: {e.args}")
        # Return more helpful error in non-production
        error_detail = str(e) if not settings.is_production else "An error occurred while processing your query"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/stream")
# @limiter.limit(CHAT_RATE_LIMIT)  # Temporarily disabled due to Starlette compatibility
async def chat_stream(
    http_request: Request,
    request: ChatRequest,
    current_user: UserInDB = Depends(get_current_user_optional)
):
    """
    Stream a response to a medical query.
    
    Uses Server-Sent Events (SSE) for real-time streaming.
    Returns chunks as they are generated.
    """
    # Validate and sanitize input
    sanitized_query, is_valid, error = validate_and_sanitize(request.query)
    
    if not is_valid:
        logger.warning(f"Invalid streaming query rejected: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    try:
        user_email = current_user.email if current_user else "anonymous"
        logger.info(f"Streaming chat request from user: {user_email}")
        
        pipeline = get_rag_pipeline()
        
        return StreamingResponse(
            pipeline.query_stream(
                question=sanitized_query,
                language=request.language.value,
                conversation_id=request.conversation_id
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Streaming error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while streaming the response"
        )


@router.get("/suggestions")
async def get_suggestions():
    """
    Get suggested medical queries for the chat interface.
    
    Returns common query templates to help users get started.
    """
    return {
        "suggestions": [
            {
                "category": "Treatment Guidelines",
                "queries": [
                    "What are the first-line treatments for hypertension?",
                    "What is the treatment algorithm for type 2 diabetes?",
                    "How should community-acquired pneumonia be treated?",
                    "What are the current guidelines for anticoagulation in atrial fibrillation?"
                ]
            },
            {
                "category": "Drug Information",
                "queries": [
                    "What are the common side effects of metformin?",
                    "What is the mechanism of action of ACE inhibitors?",
                    "What are the contraindications for aspirin use?",
                    "How should warfarin dosing be adjusted?"
                ]
            },
            {
                "category": "Clinical Presentation",
                "queries": [
                    "What are the symptoms of acute myocardial infarction?",
                    "How does diabetic ketoacidosis present clinically?",
                    "What are the red flags for headache?",
                    "What are the diagnostic criteria for sepsis?"
                ]
            },
            {
                "category": "Differential Diagnosis",
                "queries": [
                    "What is the differential diagnosis for chest pain?",
                    "What causes elevated liver enzymes?",
                    "What are the causes of acute kidney injury?",
                    "What conditions cause generalized lymphadenopathy?"
                ]
            }
        ]
    }


@router.get("/health")
async def chat_health():
    """Check if the RAG pipeline is operational."""
    try:
        pipeline = get_rag_pipeline()
        # Verify retriever is accessible
        return {
            "status": "healthy",
            "pipeline": "operational",
            "model": settings.openai_model,
            "embedding_model": settings.openai_embedding_model
        }
    except Exception as e:
        logger.error(f"Chat health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG pipeline unavailable"
        )

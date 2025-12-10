"""Drug interaction API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.api.deps import get_current_user_optional
from app.models.schemas import (
    DrugCheckRequest, DrugCheckResponse, DrugInteraction,
    Drug, InteractionSeverity, UserInDB
)
from app.services.drug_service import DrugInteractionService


router = APIRouter()

# Initialize drug service
drug_service = DrugInteractionService()


@router.post("/check-interactions", response_model=DrugCheckResponse)
async def check_drug_interactions(
    request: DrugCheckRequest,
    current_user: UserInDB = Depends(get_current_user_optional)
):
    """
    Check for interactions between multiple drugs.
    
    Returns all potential interactions with severity levels,
    clinical effects, and management recommendations.
    """
    try:
        logger.info(f"Checking interactions for: {request.drugs}")
        
        result = await drug_service.check_interactions(request.drugs)
        
        # TODO: Log to database for audit
        
        return result
        
    except Exception as e:
        logger.error(f"Drug interaction check error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while checking drug interactions"
        )


@router.get("/search")
async def search_drugs(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search the drug database by name or class.
    
    Returns matching drugs with generic names, brand names, and drug class.
    """
    try:
        results = await drug_service.search_drugs(q, limit)
        return {"drugs": results, "query": q, "count": len(results)}
        
    except Exception as e:
        logger.error(f"Drug search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching drugs"
        )


@router.get("/{drug_name}")
async def get_drug_info(drug_name: str):
    """
    Get detailed information about a specific drug.
    
    Returns drug details including mechanism, indications,
    contraindications, and common interactions.
    """
    try:
        drug_info = await drug_service.get_drug_info(drug_name)
        
        if not drug_info:
            raise HTTPException(
                status_code=404,
                detail=f"Drug '{drug_name}' not found"
            )
        
        return drug_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drug info error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching drug information"
        )


@router.get("/{drug_name}/alternatives")
async def get_drug_alternatives(
    drug_name: str,
    reason: str = Query(None, description="Reason for seeking alternatives")
):
    """
    Get alternative medications for a specific drug.
    
    Useful when a patient cannot take a particular medication
    due to allergies, interactions, or contraindications.
    """
    try:
        alternatives = await drug_service.get_alternatives(drug_name, reason)
        return {
            "drug": drug_name,
            "reason": reason,
            "alternatives": alternatives
        }
        
    except Exception as e:
        logger.error(f"Drug alternatives error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching alternatives"
        )


"""Medical codes API routes - ICD-10, SNOMED-CT lookups."""
from typing import List
from fastapi import APIRouter, Query, HTTPException
from loguru import logger

from app.models.schemas import (
    ICD10Code, SNOMEDConcept, MedicalTermTranslation,
    CodeSearchRequest, TranslationRequest, Language
)
from app.services.medical_codes import MedicalCodeService


router = APIRouter()

# Initialize service
code_service = MedicalCodeService()


@router.get("/icd10/search", response_model=List[ICD10Code])
async def search_icd10(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """
    Search ICD-10 diagnostic codes.
    
    Search by code or description. Returns matching ICD-10 codes
    with full descriptions and categories.
    """
    try:
        results = await code_service.search_icd10(q, limit)
        return results
        
    except Exception as e:
        logger.error(f"ICD-10 search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching ICD-10 codes"
        )


@router.get("/icd10/{code}", response_model=ICD10Code)
async def get_icd10_code(code: str):
    """
    Get detailed information about a specific ICD-10 code.
    
    Returns the code with full description, category information,
    and related codes.
    """
    try:
        result = await code_service.get_icd10_code(code)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"ICD-10 code '{code}' not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ICD-10 lookup error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching ICD-10 code"
        )


@router.get("/snomed/search", response_model=List[SNOMEDConcept])
async def search_snomed(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """
    Search SNOMED-CT clinical terms.
    
    Search by concept ID or term. Returns matching SNOMED concepts
    with semantic types and synonyms.
    """
    try:
        results = await code_service.search_snomed(q, limit)
        return results
        
    except Exception as e:
        logger.error(f"SNOMED search error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching SNOMED codes"
        )


@router.get("/snomed/{concept_id}", response_model=SNOMEDConcept)
async def get_snomed_concept(concept_id: str):
    """
    Get detailed information about a specific SNOMED-CT concept.
    """
    try:
        result = await code_service.get_snomed_concept(concept_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"SNOMED concept '{concept_id}' not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SNOMED lookup error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching SNOMED concept"
        )


@router.get("/translate", response_model=MedicalTermTranslation)
async def translate_medical_term(
    term: str = Query(..., description="Medical term to translate"),
    from_lang: Language = Query(Language.JAPANESE, alias="from", description="Source language"),
    to_lang: Language = Query(Language.ENGLISH, alias="to", description="Target language"),
    include_explanation: bool = Query(True, description="Include layman explanation")
):
    """
    Translate medical terms between Japanese and English.
    
    Also provides layman's explanation and related ICD-10 codes
    when available.
    """
    try:
        result = await code_service.translate_term(
            term=term,
            from_language=from_lang,
            to_language=to_lang,
            include_explanation=include_explanation
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while translating the term"
        )


@router.post("/translate", response_model=MedicalTermTranslation)
async def translate_medical_term_post(request: TranslationRequest):
    """
    Translate medical terms (POST version for complex requests).
    """
    try:
        result = await code_service.translate_term(
            term=request.term,
            from_language=request.from_language,
            to_language=request.to_language,
            include_explanation=request.include_explanation
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while translating the term"
        )


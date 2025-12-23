"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ==================== Enums ====================

class UserRole(str, Enum):
    """User role types for RBAC."""
    DOCTOR = "doctor"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    ADMIN = "admin"


class QueryType(str, Enum):
    """Types of queries for audit logging."""
    CHAT = "chat"
    DRUG_CHECK = "drug_check"
    CODE_LOOKUP = "code_lookup"
    SEARCH = "search"


class InteractionSeverity(str, Enum):
    """Drug interaction severity levels."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CONTRAINDICATED = "contraindicated"


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    JAPANESE = "ja"


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str
    role: UserRole = UserRole.DOCTOR
    organization: Optional[str] = None
    license_number: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)


class UserInDB(UserBase):
    """User schema with database fields."""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User response schema (public data only)."""
    id: str


# ==================== Auth Schemas ====================

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=86400, description="Token expiry in seconds")
    user: UserResponse


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # User ID
    email: str
    role: str
    exp: datetime


# ==================== Citation & Source Schemas ====================

class Citation(BaseModel):
    """Citation for a medical source."""
    id: int
    title: str
    authors: Optional[List[str]] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    url: Optional[str] = None
    snippet: str  # Relevant excerpt from the source
    relevance_score: float = Field(..., ge=0, le=1)


class Source(BaseModel):
    """Source document from vector search."""
    content: str
    metadata: Dict[str, Any]
    score: float


# ==================== Chat Schemas ====================

class ChatRequest(BaseModel):
    """Chat query request."""
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    language: Language = Language.ENGLISH
    include_sources: bool = True


class ChatResponse(BaseModel):
    """Chat response with RAG-generated answer."""
    model_config = ConfigDict(protected_namespaces=())
    
    answer: str
    sources: List[Citation]
    conversation_id: str
    query_id: str
    processing_time_ms: int
    model_used: str


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    type: str  # "content", "source", "done", "error"
    content: Optional[str] = None
    source: Optional[Citation] = None
    error: Optional[str] = None


# ==================== Drug Interaction Schemas ====================

class Drug(BaseModel):
    """Drug information."""
    name: str
    generic_name: Optional[str] = None
    brand_names: List[str] = []
    drug_class: Optional[str] = None
    description: Optional[str] = None


class DrugInteraction(BaseModel):
    """Drug interaction details."""
    drug_a: str
    drug_b: str
    severity: InteractionSeverity
    description: str
    mechanism: Optional[str] = None
    management: Optional[str] = None
    clinical_effects: List[str] = []
    source: Optional[str] = None


class DrugCheckRequest(BaseModel):
    """Request to check drug interactions."""
    drugs: List[str] = Field(..., min_length=2, max_length=20)


class DrugCheckResponse(BaseModel):
    """Drug interaction check response."""
    interactions: List[DrugInteraction]
    alternatives: List[Drug] = []
    warnings: List[str] = []
    checked_drugs: List[str]
    has_severe_interactions: bool
    has_contraindications: bool


class DrugSearchRequest(BaseModel):
    """Drug search request."""
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


# ==================== Medical Code Schemas ====================

class ICD10Code(BaseModel):
    """ICD-10 diagnostic code."""
    code: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    includes: List[str] = []
    excludes: List[str] = []


class SNOMEDConcept(BaseModel):
    """SNOMED-CT concept."""
    concept_id: str
    term: str
    semantic_type: Optional[str] = None
    synonyms: List[str] = []


class MedicalTermTranslation(BaseModel):
    """Medical term translation between languages."""
    original_term: str
    translated_term: str
    from_language: Language
    to_language: Language
    medical_context: Optional[str] = None
    icd10_codes: List[str] = []
    layman_explanation: Optional[str] = None


class CodeSearchRequest(BaseModel):
    """Medical code search request."""
    query: str = Field(..., min_length=1)
    limit: int = Field(default=20, ge=1, le=100)


class TranslationRequest(BaseModel):
    """Translation request."""
    term: str
    from_language: Language
    to_language: Language
    include_explanation: bool = True


# ==================== History Schemas ====================

class QueryLog(BaseModel):
    """Query log entry for audit."""
    id: str
    user_id: str
    query_text: str
    response_text: Optional[str] = None
    sources: List[Citation] = []
    query_type: QueryType
    response_time_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SavedQuery(BaseModel):
    """Saved/bookmarked query."""
    id: str
    query_log_id: str
    title: str
    notes: Optional[str] = None
    query: QueryLog
    created_at: datetime


class BookmarkRequest(BaseModel):
    """Request to bookmark a query."""
    title: str = Field(..., max_length=255)
    notes: Optional[str] = None


class HistoryResponse(BaseModel):
    """Paginated history response."""
    items: List[QueryLog]
    total: int
    page: int
    page_size: int
    has_more: bool


# ==================== Search Schemas ====================

class SearchRequest(BaseModel):
    """Direct search request."""
    query: str = Field(..., min_length=1)
    search_type: str = "hybrid"  # "semantic", "keyword", "hybrid"
    filters: Dict[str, Any] = {}
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    """Search result item."""
    id: str
    content: str
    title: Optional[str] = None
    source_type: str  # "paper", "guideline", "drug_info"
    metadata: Dict[str, Any]
    score: float


class SearchResponse(BaseModel):
    """Search response."""
    results: List[SearchResult]
    total: int
    query: str
    search_type: str


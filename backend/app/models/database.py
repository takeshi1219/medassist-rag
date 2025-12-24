"""SQLAlchemy database models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey,
    JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """Healthcare provider user model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='doctor')  # doctor, nurse, pharmacist, admin
    organization = Column(String(255), nullable=True)
    license_number = Column(String(100), nullable=True)
    is_active = Column(String(10), default='true')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    query_logs = relationship("QueryLog", back_populates="user", cascade="all, delete-orphan")
    saved_queries = relationship("SavedQuery", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class QueryLog(Base):
    """Audit log for all queries."""
    __tablename__ = "query_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    sources = Column(JSON)  # Array of citation objects
    query_type = Column(String(50), nullable=False)  # chat, drug_check, code_lookup, search
    response_time_ms = Column(Integer)
    model_used = Column(String(100))
    language = Column(String(10), default='en')
    conversation_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="query_logs")
    saved_query = relationship("SavedQuery", back_populates="query_log", uselist=False)
    
    __table_args__ = (
        Index('ix_query_logs_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<QueryLog {self.id}>"


class SavedQuery(Base):
    """Bookmarked/saved queries."""
    __tablename__ = "saved_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    query_log_id = Column(UUID(as_uuid=True), ForeignKey('query_logs.id'), nullable=False)
    title = Column(String(255), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_queries")
    query_log = relationship("QueryLog", back_populates="saved_query")
    
    def __repr__(self):
        return f"<SavedQuery {self.title}>"


class DrugInteractionCache(Base):
    """Cached drug interactions for faster lookups."""
    __tablename__ = "drug_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drug_a = Column(String(255), nullable=False, index=True)
    drug_b = Column(String(255), nullable=False, index=True)
    severity = Column(String(50), nullable=False)  # none, mild, moderate, severe, contraindicated
    description = Column(Text, nullable=False)
    mechanism = Column(Text)
    management = Column(Text)
    clinical_effects = Column(JSON)  # List of effects
    source = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('drug_a', 'drug_b', name='uq_drug_pair'),
        Index('ix_drug_interactions_drugs', 'drug_a', 'drug_b'),
    )
    
    def __repr__(self):
        return f"<DrugInteraction {self.drug_a} + {self.drug_b}>"


class MedicalCode(Base):
    """Medical codes (ICD-10, SNOMED-CT) cache."""
    __tablename__ = "medical_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_type = Column(String(50), nullable=False)  # 'icd10', 'snomed'
    code = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    description_ja = Column(Text)  # Japanese translation
    category = Column(String(255))
    parent_code = Column(String(100))
    extra_data = Column(JSON)  # renamed from 'metadata' - reserved in SQLAlchemy
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('code_type', 'code', name='uq_medical_code'),
        Index('ix_medical_codes_search', 'code_type', 'code', 'description'),
    )
    
    def __repr__(self):
        return f"<MedicalCode {self.code_type}:{self.code}>"


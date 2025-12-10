"""Application configuration using Pydantic Settings."""
import os
import secrets
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "MedAssist RAG"
    app_version: str = "1.0.0"
    environment: str = "production"  # Default to production for safety
    debug: bool = False  # Default to False for safety
    secret_key: str = ""  # Must be set in environment
    
    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: str = ""  # Must be explicitly set
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Pinecone
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "medassist"
    
    # Chroma (local alternative)
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    use_chroma: bool = False
    
    # Database
    database_url: str = ""
    
    # Redis
    redis_url: str = ""
    
    # Supabase (for production auth)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Rate Limiting
    rate_limit_per_minute: int = 30  # Conservative default
    rate_limit_burst: int = 10
    
    # Security
    max_query_length: int = 2000  # Max characters for medical queries
    session_expiry_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    enable_audit_log: bool = True  # HIPAA audit logging
    
    # Feature Flags
    enable_demo_mode: bool = False  # Must explicitly enable demo
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure secret key is set in production."""
        if not v:
            # Generate a random key for development, but warn
            env = os.getenv('ENVIRONMENT', 'production')
            if env == 'development':
                return secrets.token_urlsafe(32)
            raise ValueError("SECRET_KEY must be set in production environment")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
    
    @field_validator('allowed_origins')
    @classmethod
    def validate_allowed_origins(cls, v: str, info) -> str:
        """Set default origins based on environment."""
        if not v:
            env = os.getenv('ENVIRONMENT', 'production')
            if env == 'development':
                return "http://localhost:3000"
            # In production, must be explicitly set
            return ""
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def docs_enabled(self) -> bool:
        """Only enable API docs in development."""
        return self.is_development or self.debug
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

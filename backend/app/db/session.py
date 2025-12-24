"""Database session management."""
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool
from loguru import logger

from app.config import settings
from app.models.database import Base


# Convert sync URL to async
def get_async_database_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg://"""
    if not url:
        return ""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# Create async engine only if DATABASE_URL is set
engine: Optional[AsyncEngine] = None
async_session: Optional[async_sessionmaker] = None

if settings.database_url:
    database_url = get_async_database_url(settings.database_url)
    logger.info(f"Connecting to database...")
    
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        poolclass=NullPool,  # Disable pooling for async
    )
    
    # Create async session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
else:
    logger.warning("DATABASE_URL not set - database features disabled")


async def init_db():
    """Initialize database and create tables."""
    if not engine:
        logger.warning("No database configured - skipping initialization")
        return
        
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


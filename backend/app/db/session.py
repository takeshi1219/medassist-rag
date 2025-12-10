"""Database session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from loguru import logger

from app.config import settings
from app.models.database import Base


# Convert sync URL to async
def get_async_database_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg://"""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Create async engine
engine = create_async_engine(
    get_async_database_url(settings.database_url),
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


async def init_db():
    """Initialize database and create tables."""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
        logger.info("Continuing without database - some features may be limited")


async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


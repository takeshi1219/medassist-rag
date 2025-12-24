"""User service for database operations."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import uuid

from app.models.database import User


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email address."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    try:
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(
            select(User).where(User.id == user_uuid)
        )
        return result.scalar_one_or_none()
    except ValueError:
        return None


async def create_user(
    db: AsyncSession,
    email: str,
    name: str,
    hashed_password: str,
    role: str = "doctor",
    organization: Optional[str] = None,
    license_number: Optional[str] = None
) -> User:
    """Create a new user."""
    user = User(
        email=email,
        name=name,
        hashed_password=hashed_password,
        role=role,
        organization=organization,
        license_number=license_number
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"Created new user: {email}")
    return user


async def update_user(
    db: AsyncSession,
    user: User,
    name: Optional[str] = None,
    organization: Optional[str] = None,
    license_number: Optional[str] = None
) -> User:
    """Update user profile."""
    if name is not None:
        user.name = name
    if organization is not None:
        user.organization = organization
    if license_number is not None:
        user.license_number = license_number
    
    await db.commit()
    await db.refresh(user)
    return user


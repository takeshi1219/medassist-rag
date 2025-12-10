"""API Dependencies for dependency injection."""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from loguru import logger
from datetime import datetime, timezone

from app.config import settings
from app.db.session import async_session
from app.models.schemas import UserInDB
from app.middleware.audit import audit_logger


security = HTTPBearer(auto_error=True)
security_optional = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise credentials_exception


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserInDB:
    """
    Validate JWT token and return current user.
    
    In development with demo mode enabled, returns a mock user.
    In production, validates JWT and fetches user from database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    # Demo mode for development only
    if settings.is_development and settings.enable_demo_mode:
        logger.debug("Using demo authentication mode")
        return UserInDB(
            id="demo-user-123",
            email="demo@medassist.com",
            name="Dr. Demo User",
            role="doctor",
            organization="Demo Hospital",
            license_number="MD123456"
        )
    
    # Production authentication
    try:
        payload = await verify_jwt_token(token)
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role", "user")
        
        if user_id is None:
            raise credentials_exception
        
        # In a full implementation, fetch user from database:
        # user = await get_user_by_id(db, user_id)
        # if user is None:
        #     raise credentials_exception
        # return user
        
        # For now, construct user from JWT claims
        user = UserInDB(
            id=user_id,
            email=email or "unknown@example.com",
            name=payload.get("name", "Healthcare Provider"),
            role=role,
            organization=payload.get("organization"),
            license_number=payload.get("license_number")
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserInDB]:
    """Get current user if token is provided, else return None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        return None


def require_role(allowed_roles: list[str]):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(user: UserInDB = Depends(require_role(["admin"]))):
            ...
    """
    async def role_checker(
        current_user: UserInDB = Depends(get_current_user)
    ) -> UserInDB:
        if current_user.role not in allowed_roles:
            logger.warning(
                f"Access denied for user {current_user.id} "
                f"with role {current_user.role} (required: {allowed_roles})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized for this action"
            )
        return current_user
    return role_checker


def require_admin():
    """Shortcut for requiring admin role."""
    return require_role(["admin"])


def require_doctor():
    """Shortcut for requiring doctor or admin role."""
    return require_role(["doctor", "admin"])

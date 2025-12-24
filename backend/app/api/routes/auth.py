"""Authentication API routes (Production Ready)."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from jose import jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.config import settings
from app.api.deps import get_current_user, get_db
from app.models.schemas import (
    LoginRequest, LoginResponse, UserCreate,
    UserResponse, UserInDB
)
from app.middleware.audit import audit_logger
from app.middleware.rate_limit import limiter, AUTH_RATE_LIMIT
from app.services.user_service import get_user_by_email, create_user


router = APIRouter()


def create_access_token(
    data: dict,
    expires_delta: timedelta = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data to encode
        expires_delta: Token expiry time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=settings.session_expiry_hours)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": settings.app_name
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def hash_password(password: str) -> str:
    """Hash a password securely using bcrypt."""
    # Encode and hash with bcrypt
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


@router.post("/login", response_model=LoginResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def login(
    request: Request,
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    In development with demo mode, accepts any credentials.
    In production, validates against database.
    """
    # Demo mode for development only
    if settings.is_development and settings.enable_demo_mode:
        logger.info(f"Demo login for: {login_request.email}")
        
        user = UserResponse(
            id="demo-user-123",
            email=login_request.email,
            name="Dr. Demo User",
            role="doctor",
            organization="Demo Hospital"
        )
        
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "organization": user.organization
            }
        )
        
        audit_logger.log_auth_event(
            event_type="LOGIN",
            email=login_request.email,
            success=True,
            request=request
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.session_expiry_hours * 3600,
            user=user
        )
    
    # Production authentication - database lookup
    db_user = await get_user_by_email(db, login_request.email)
    
    if not db_user or not verify_password(login_request.password, db_user.hashed_password):
        audit_logger.log_auth_event(
            event_type="FAILED_LOGIN",
            email=login_request.email,
            success=False,
            request=request,
            reason="Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if db_user.is_active != 'true':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Create response user
    user = UserResponse(
        id=str(db_user.id),
        email=db_user.email,
        name=db_user.name,
        role=db_user.role,
        organization=db_user.organization,
        license_number=db_user.license_number
    )
    
    access_token = create_access_token(
        data={
            "sub": str(db_user.id),
            "email": db_user.email,
            "name": db_user.name,
            "role": db_user.role,
            "organization": db_user.organization
        }
    )
    
    audit_logger.log_auth_event(
        event_type="LOGIN",
        email=login_request.email,
        success=True,
        request=request
    )
    
    logger.info(f"User logged in: {login_request.email}")
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.session_expiry_hours * 3600,
        user=user
    )


@router.post("/register", response_model=UserResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new healthcare provider account.
    
    In development with demo mode, returns a mock user.
    In production, creates user in database with proper validation.
    """
    # Validate email format
    if not user_data.email or "@" not in user_data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Demo mode
    if settings.is_development and settings.enable_demo_mode:
        logger.info(f"Demo registration for: {user_data.email}")
        
        return UserResponse(
            id=f"user-{hash(user_data.email) % 1000000}",
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            organization=user_data.organization,
            license_number=user_data.license_number
        )
    
    # Production registration - check if user exists
    try:
        existing = await get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        db_user = await create_user(
            db=db,
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            role=user_data.role or "doctor",
            organization=user_data.organization,
            license_number=user_data.license_number
        )
        
        logger.info(f"New user registered: {user_data.email}")
        
        return UserResponse(
            id=str(db_user.id),
            email=db_user.email,
            name=db_user.name,
            role=db_user.role,
            organization=db_user.organization,
            license_number=db_user.license_number
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {user_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Logout user.
    
    In a production system with Redis:
    1. Add the token to a blacklist
    2. Clear any server-side session data
    """
    audit_logger.log_auth_event(
        event_type="LOGOUT",
        email=current_user.email,
        success=True,
        request=request
    )
    
    logger.info(f"User logged out: {current_user.email}")
    
    # TODO: Add token to Redis blacklist
    # await redis_client.setex(
    #     f"blacklist:{token}",
    #     settings.session_expiry_hours * 3600,
    #     "1"
    # )
    
    return {"message": "Successfully logged out"}


@router.post("/refresh")
@limiter.limit(AUTH_RATE_LIMIT)
async def refresh_token(
    request: Request,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Refresh access token.
    
    Issues a new token with extended expiry.
    """
    new_token = create_access_token(
        data={
            "sub": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "organization": current_user.organization
        }
    )
    
    audit_logger.log_auth_event(
        event_type="TOKEN_REFRESH",
        email=current_user.email,
        success=True,
        request=request
    )
    
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": settings.session_expiry_hours * 3600
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        organization=current_user.organization,
        license_number=current_user.license_number
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    name: str = None,
    organization: str = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update current user's profile."""
    # TODO: Implement database update
    # updated = await update_user(db, current_user.id, name=name, organization=organization)
    # return updated
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=name or current_user.name,
        role=current_user.role,
        organization=organization or current_user.organization,
        license_number=current_user.license_number
    )

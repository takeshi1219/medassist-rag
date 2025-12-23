"""Rate limiting middleware using SlowAPI."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request
from loguru import logger

from app.config import settings


def get_client_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    
    Uses authenticated user ID if available, otherwise IP address.
    """
    # Try to get user from token (if authenticated)
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        # Use a hash of the token for rate limiting
        token = auth_header[7:]
        return f"user:{hash(token) % 1000000}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    storage_uri=settings.redis_url if settings.redis_url else None,
    strategy="fixed-window"
)


def setup_rate_limiter(app: FastAPI) -> None:
    """
    Configure rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # NOTE: SlowAPIMiddleware disabled due to Starlette compatibility issues
    # The @limiter.limit decorator still works on individual endpoints
    # app.add_middleware(SlowAPIMiddleware)
    
    logger.info(
        f"Rate limiting configured: {settings.rate_limit_per_minute}/minute, "
        f"burst: {settings.rate_limit_burst}"
    )


# Decorator for custom rate limits on specific endpoints
def rate_limit(limit: str):
    """
    Custom rate limit decorator for specific endpoints.
    
    Usage:
        @router.get("/expensive-operation")
        @rate_limit("5/minute")
        async def expensive_operation():
            ...
    """
    return limiter.limit(limit)


# Stricter limits for sensitive operations
CHAT_RATE_LIMIT = f"{settings.rate_limit_per_minute}/minute"
AUTH_RATE_LIMIT = "10/minute"  # Stricter for auth endpoints
SEARCH_RATE_LIMIT = "60/minute"  # More lenient for search


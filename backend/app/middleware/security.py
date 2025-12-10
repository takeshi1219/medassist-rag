"""Security headers middleware for production hardening."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Implements OWASP security header recommendations.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (restrict browser features)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=()"
        )
        
        # Content Security Policy (production only)
        if settings.is_production:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'"
            )
            
            # HSTS - enforce HTTPS
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate incoming requests for security concerns.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request size (prevent DoS)
        content_length = request.headers.get("content-length")
        if content_length:
            max_size = 1024 * 1024  # 1MB max
            if int(content_length) > max_size:
                return Response(
                    content='{"detail": "Request too large"}',
                    status_code=413,
                    media_type="application/json"
                )
        
        # Block suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        blocked_agents = ["sqlmap", "nikto", "nmap", "masscan"]
        if any(agent in user_agent for agent in blocked_agents):
            return Response(
                content='{"detail": "Forbidden"}',
                status_code=403,
                media_type="application/json"
            )
        
        return await call_next(request)


"""Security headers middleware for production hardening."""
from starlette.responses import Response
from starlette.datastructures import MutableHeaders

from app.config import settings


class SecurityHeadersMiddleware:
    """
    Pure ASGI middleware to add security headers to all responses.
    Implements OWASP security header recommendations.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(raw=list(message.get("headers", [])))
                
                # Prevent clickjacking
                headers["X-Frame-Options"] = "DENY"
                # Prevent MIME type sniffing
                headers["X-Content-Type-Options"] = "nosniff"
                # Enable XSS filter
                headers["X-XSS-Protection"] = "1; mode=block"
                # Referrer policy
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                # Permissions policy
                headers["Permissions-Policy"] = (
                    "geolocation=(), microphone=(), camera=(), "
                    "payment=(), usb=(), magnetometer=()"
                )
                
                if settings.is_production:
                    headers["Content-Security-Policy"] = (
                        "default-src 'self'; script-src 'self'; "
                        "style-src 'self' 'unsafe-inline'; "
                        "img-src 'self' data: https:; font-src 'self'; "
                        "connect-src 'self'"
                    )
                    headers["Strict-Transport-Security"] = (
                        "max-age=31536000; includeSubDomains; preload"
                    )
                
                message["headers"] = headers.raw
            
            await send(message)
        
        await self.app(scope, receive, send_with_headers)


class RequestValidationMiddleware:
    """
    Pure ASGI middleware to validate incoming requests for security.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        headers = dict(scope.get("headers", []))
        
        # Check request size (prevent DoS)
        content_length = headers.get(b"content-length", b"").decode()
        if content_length:
            max_size = 1024 * 1024  # 1MB max
            try:
                if int(content_length) > max_size:
                    response = Response(
                        content='{"detail": "Request too large"}',
                        status_code=413,
                        media_type="application/json"
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass
        
        # Block suspicious user agents
        user_agent = headers.get(b"user-agent", b"").decode().lower()
        blocked_agents = ["sqlmap", "nikto", "nmap", "masscan"]
        if any(agent in user_agent for agent in blocked_agents):
            response = Response(
                content='{"detail": "Forbidden"}',
                status_code=403,
                media_type="application/json"
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)


"""HIPAA-compliant audit logging for medical data access."""
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
import sys

from app.config import settings


class AuditLogger:
    """
    HIPAA-compliant audit logger for tracking PHI access.
    
    Logs are structured for compliance reporting and include:
    - Who: User identity
    - What: Action performed
    - When: Timestamp
    - Where: Source IP, endpoint
    - Why: Request context
    - Outcome: Success/failure
    """
    
    def __init__(self):
        """Initialize audit logger with dedicated log file."""
        self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """Configure dedicated audit log handler."""
        # Remove default handler for audit logs
        self.audit_logger = logger.bind(audit=True)
        
        # Add audit-specific sink if enabled
        if settings.enable_audit_log:
            logger.add(
                "logs/audit_{time:YYYY-MM-DD}.log",
                rotation="1 day",
                retention="2 years",  # HIPAA requires 6 years, adjust as needed
                format="{message}",
                filter=lambda record: record["extra"].get("audit", False),
                level="INFO",
                serialize=True
            )
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        request: Request,
        response_status: int,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a PHI access event.
        
        Args:
            user_id: Authenticated user identifier
            action: Action performed (QUERY, VIEW, EXPORT, etc.)
            resource: Resource accessed (chat, drug-check, etc.)
            request: HTTP request object
            response_status: HTTP response status code
            details: Additional context (sanitized, no PHI)
        """
        if not settings.enable_audit_log:
            return
        
        audit_record = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "PHI_ACCESS",
            
            # Who
            "user_id": user_id,
            "user_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown")[:200],
            
            # What
            "action": action,
            "resource": resource,
            "method": request.method,
            "endpoint": str(request.url.path),
            
            # Outcome
            "status_code": response_status,
            "success": 200 <= response_status < 400,
            
            # Context (sanitized)
            "details": self._sanitize_details(details or {}),
            
            # Environment
            "environment": settings.environment,
            "app_version": settings.app_version
        }
        
        # Log as structured JSON
        self.audit_logger.info(json.dumps(audit_record))
    
    def log_access_from_info(
        self,
        request_info: Dict[str, Any],
        action: str,
        resource: str,
        response_status: int,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a PHI access event from pre-extracted request info.
        Used by ASGI middleware where Request object isn't available.
        """
        if not settings.enable_audit_log:
            return
        
        audit_record = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "PHI_ACCESS",
            
            # Who
            "user_id": request_info.get("user_id", "unknown"),
            "user_ip": request_info.get("user_ip", "unknown"),
            "user_agent": request_info.get("user_agent", "unknown"),
            
            # What
            "action": action,
            "resource": resource,
            "method": request_info.get("method", ""),
            "endpoint": request_info.get("path", ""),
            
            # Outcome
            "status_code": response_status,
            "success": 200 <= response_status < 400,
            
            # Context (sanitized)
            "details": self._sanitize_details(details or {}),
            
            # Environment
            "environment": settings.environment,
            "app_version": settings.app_version
        }
        
        # Log as structured JSON
        self.audit_logger.info(json.dumps(audit_record))
    
    def log_auth_event(
        self,
        event_type: str,
        email: str,
        success: bool,
        request: Request,
        reason: Optional[str] = None
    ):
        """
        Log authentication events.
        
        Args:
            event_type: LOGIN, LOGOUT, FAILED_LOGIN, TOKEN_REFRESH
            email: User email (will be partially masked)
            success: Whether auth succeeded
            request: HTTP request object
            reason: Failure reason if applicable
        """
        if not settings.enable_audit_log:
            return
        
        audit_record = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": f"AUTH_{event_type}",
            
            "user_email_masked": self._mask_email(email),
            "user_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown")[:200],
            
            "success": success,
            "reason": reason,
            
            "environment": settings.environment
        }
        
        self.audit_logger.info(json.dumps(audit_record))
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check for forwarded headers (behind load balancer)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _mask_email(self, email: str) -> str:
        """Partially mask email for privacy."""
        if "@" not in email:
            return "***"
        local, domain = email.rsplit("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove any potential PHI from details."""
        sanitized = {}
        
        # Allowed fields only
        allowed_keys = {
            "query_length", "response_time_ms", "source_count",
            "model_used", "language", "feature_used"
        }
        
        for key, value in details.items():
            if key in allowed_keys:
                sanitized[key] = value
        
        return sanitized


class AuditMiddleware:
    """
    Pure ASGI Middleware for HIPAA-compliant audit logging.
    Using pure ASGI instead of BaseHTTPMiddleware for better compatibility.
    """
    
    # Endpoints that access PHI and require audit logging
    PHI_ENDPOINTS = {
        "/api/v1/chat": "MEDICAL_QUERY",
        "/api/v1/drugs": "DRUG_CHECK",
        "/api/v1/search": "MEDICAL_SEARCH",
        "/api/v1/codes": "CODE_LOOKUP",
        "/api/v1/history": "HISTORY_ACCESS"
    }
    
    def __init__(self, app, audit_logger: AuditLogger):
        self.app = app
        self.audit_logger = audit_logger
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Skip OPTIONS requests (CORS preflight)
        if scope.get("method") == "OPTIONS":
            await self.app(scope, receive, send)
            return
        
        # Check if this endpoint needs audit logging
        path = scope.get("path", "")
        action = None
        for endpoint_prefix, action_type in self.PHI_ENDPOINTS.items():
            if path.startswith(endpoint_prefix):
                action = action_type
                break
        
        # Extract request info BEFORE processing (while scope is valid)
        request_info = None
        if action and settings.enable_audit_log:
            request_info = self._extract_request_info(scope)
        
        # Capture response status
        response_status = 200
        
        async def send_wrapper(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 200)
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
        
        # Log if PHI endpoint was accessed
        if action and request_info:
            try:
                self.audit_logger.log_access_from_info(
                    request_info=request_info,
                    action=action,
                    resource=path,
                    response_status=response_status
                )
            except Exception as e:
                logger.warning(f"Audit logging failed: {e}")
    
    def _extract_request_info(self, scope) -> Dict[str, Any]:
        """Extract request info from ASGI scope before processing."""
        headers = dict(scope.get("headers", []))
        
        # Get client IP
        forwarded = headers.get(b"x-forwarded-for", b"").decode()
        real_ip = headers.get(b"x-real-ip", b"").decode()
        client = scope.get("client", ("unknown", 0))
        
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif real_ip:
            client_ip = real_ip
        else:
            client_ip = client[0] if client else "unknown"
        
        # Get auth header for user ID extraction
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            user_id = f"user_{hash(auth_header[7:]) % 1000000}"
        else:
            user_id = "anonymous"
        
        return {
            "user_id": user_id,
            "user_ip": client_ip,
            "user_agent": headers.get(b"user-agent", b"unknown").decode()[:200],
            "method": scope.get("method", ""),
            "path": scope.get("path", ""),
        }


# Singleton instance
audit_logger = AuditLogger()


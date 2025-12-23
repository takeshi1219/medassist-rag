"""MedAssist RAG - FastAPI Application Entry Point (Production Ready)."""
import time
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import redis.asyncio as redis

from app.config import settings
from app.api.routes import chat, drugs, search, auth, codes, history
from app.db.session import init_db, engine
from app.middleware.security import SecurityHeadersMiddleware, RequestValidationMiddleware
from app.middleware.rate_limit import setup_rate_limiter, limiter
from app.middleware.audit import AuditMiddleware, audit_logger


async def check_database_health() -> bool:
    """Check if database is accessible."""
    try:
        from sqlalchemy import text
        from app.db.session import async_session
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_redis_health() -> bool:
    """Check if Redis is accessible."""
    if not settings.redis_url:
        return True  # Redis not configured, skip check
    try:
        client = redis.from_url(settings.redis_url)
        await client.ping()
        await client.close()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


async def check_vector_store_health() -> bool:
    """Check if vector store (Pinecone) is accessible."""
    if settings.use_chroma:
        # ChromaDB check
        try:
            import chromadb
            client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port
            )
            client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB health check failed: {e}")
            return False
    else:
        # Pinecone check
        if not settings.pinecone_api_key:
            return True  # Not configured
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.pinecone_api_key)
            index = pc.Index(settings.pinecone_index_name)
            index.describe_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Validate critical settings in production
    if settings.is_production:
        if not settings.allowed_origins:
            logger.warning("ALLOWED_ORIGINS not set - CORS will block all origins")
        if settings.debug:
            logger.warning("DEBUG mode is enabled in production!")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if settings.is_production:
            raise  # Fail fast in production
    
    # Create logs directory for audit logs
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app with conditional docs
app = FastAPI(
    title=settings.app_name,
    description="AI-powered clinical decision support system using RAG",
    version=settings.app_version,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
    lifespan=lifespan,
)

# Setup rate limiting first
setup_rate_limiter(app)

# Security middleware stack
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
# AuditMiddleware is pure ASGI, add it directly
app.add_middleware(AuditMiddleware, audit_logger=audit_logger)

# CORS Middleware - MUST be added LAST so it processes requests FIRST
# This ensures OPTIONS preflight requests get CORS headers before other middleware
if settings.allowed_origins_list:
    logger.info(f"CORS configured for origins: {settings.allowed_origins_list}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],  # Allow all headers
        expose_headers=["X-Process-Time", "X-Request-ID"],
        max_age=3600,
    )
else:
    logger.warning("CORS not configured - no origins allowed")


class RequestMetadataMiddleware:
    """Pure ASGI middleware to add request ID and processing time."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        import uuid
        from starlette.datastructures import MutableHeaders
        
        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", b"").decode() or str(uuid.uuid4())
        path = scope.get("path", "")
        method = scope.get("method", "")
        
        start_time = time.time()
        response_status = 200
        
        async def send_with_metadata(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 200)
                process_time = time.time() - start_time
                
                headers = MutableHeaders(raw=list(message.get("headers", [])))
                headers["X-Process-Time"] = str(round(process_time * 1000, 2))
                headers["X-Request-ID"] = request_id
                message["headers"] = headers.raw
                
                # Log requests (exclude health checks)
                if not path.startswith("/health"):
                    logger.info(f"{method} {path} - {response_status} - {round(process_time * 1000)}ms")
            
            await send(message)
        
        await self.app(scope, receive, send_with_metadata)


# Add request metadata middleware
app.add_middleware(RequestMetadataMiddleware)


# Include API routes
app.include_router(
    auth.router,
    prefix=f"{settings.api_v1_prefix}/auth",
    tags=["Authentication"]
)
app.include_router(
    chat.router,
    prefix=f"{settings.api_v1_prefix}/chat",
    tags=["Chat / RAG"]
)
app.include_router(
    drugs.router,
    prefix=f"{settings.api_v1_prefix}/drugs",
    tags=["Drug Interactions"]
)
app.include_router(
    codes.router,
    prefix=f"{settings.api_v1_prefix}/codes",
    tags=["Medical Codes"]
)
app.include_router(
    search.router,
    prefix=f"{settings.api_v1_prefix}/search",
    tags=["Search"]
)
app.include_router(
    history.router,
    prefix=f"{settings.api_v1_prefix}/history",
    tags=["Query History"]
)


@app.get("/")
async def root():
    """Root endpoint - basic info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.docs_enabled else "disabled"
    }


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns status of all dependent services.
    """
    # Perform health checks
    db_healthy = await check_database_health()
    redis_healthy = await check_redis_health()
    vector_healthy = await check_vector_store_health()
    
    # Determine overall status
    all_healthy = db_healthy and redis_healthy and vector_healthy
    
    health_status = {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {
            "api": "up",
            "database": "up" if db_healthy else "down",
            "vector_store": "up" if vector_healthy else "down",
            "cache": "up" if redis_healthy else "down"
        }
    }
    
    # Return 503 if unhealthy (for load balancer health checks)
    if not all_healthy and settings.is_production:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe - is the app running?"""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe - can the app serve traffic?"""
    db_healthy = await check_database_health()
    if not db_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready"
        )
    return {"status": "ready"}


def get_cors_headers(request: Request) -> dict:
    """Get CORS headers for error responses."""
    origin = request.headers.get("origin", "")
    if origin in settings.allowed_origins_list:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    return {}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    # Log the full error
    logger.exception(f"Unhandled exception on {request.url.path}: {exc}")
    
    # Return sanitized error in production
    error_detail = str(exc) if settings.debug else "An internal server error occurred"
    
    # Include CORS headers for cross-origin error responses
    headers = get_cors_headers(request)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": error_detail,
            "type": "internal_error"
        },
        headers=headers
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with logging."""
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    elif exc.status_code >= 400:
        logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    
    # Merge CORS headers with any existing exception headers
    headers = get_cors_headers(request)
    if hasattr(exc, "headers") and exc.headers:
        headers.update(exc.headers)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers if headers else None
    )

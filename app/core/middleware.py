# In app/core/middleware.py
import time
import uuid
import logging
from typing import Optional, Set
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- CUSTOM MIDDLEWARE CLASSES ---

class ProfessionalLoggingMiddleware(BaseHTTPMiddleware):
    """
    A single, professional-grade middleware for request tracing and structured logging.
    """
    def __init__(self, app, exclude_paths: Optional[Set[str]] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or set()

    async def dispatch(self, request: Request, call_next):
        # 1. Generate a unique ID for the request and add it to the request state.
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        should_log = request.url.path not in self.exclude_paths
        
        if should_log:
            logger.info(
                "Request started",
                extra={
                    "request_id": request.state.request_id,
                    "method": request.method,
                    "path": request.url.path,
                }
            )
        
        # 2. Call the actual endpoint.
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        
        # 3. Add the request ID to the response headers for client-side debugging.
        response.headers["X-Request-ID"] = request_id
        
        if should_log:
            logger.info(
                "Request finished",
                extra={
                    "request_id": request.state.request_id,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time, 2),
                }
            )
            
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add essential security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# --- MIDDLEWARE REGISTRATION ---

def register_middlewares(app: FastAPI):
    """
    Registers all middlewares for the FastAPI application.
    The order is important: they process requests top-to-bottom
    and responses bottom-to-top.
    """
    # Helper to safely parse settings
    def _get_config_list(setting_name: str, default: list[str]) -> list[str]:
        config_value = getattr(settings, setting_name, None)
        if not config_value: return default
        return [item.strip() for item in config_value.split(",") if item.strip()]

    # 1. GZip Middleware (compress responses)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 2. Trusted Host Middleware (protect against host header attacks)
    allowed_hosts = _get_config_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    # 3. Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 4. CORS Middleware (allow cross-origin requests)
    cors_origins = _get_config_list("CORS_ORIGINS", ["http://localhost:3000"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 5. Our single, combined logging and request context middleware
    exclude_paths = settings.LOGGING_EXCLUDE_PATHS
    app.add_middleware(ProfessionalLoggingMiddleware, exclude_paths=exclude_paths)
    
    logger.info("All middlewares registered successfully.")

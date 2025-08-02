# # In app/core/middleware.py
# import time
# import uuid
# import logging
# import json
# from datetime import datetime
# from typing import Optional, Set
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.middleware.cors import CORSMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware
# from starlette.middleware.gzip import GZipMiddleware
# from app.core.config import settings

# # Get a logger instance
# logger = logging.getLogger(__name__)


# class ProfessionalLoggingMiddleware(BaseHTTPMiddleware):
#     """
#     A professional-grade logging middleware that adds a unique request ID
#     and logs structured information about each request with comprehensive error handling.
#     """
    
#     def __init__(self, app, exclude_paths: Optional[Set[str]] = None):
#         super().__init__(app)
#         # Exclude health check and metrics endpoints from detailed logging
#         self.exclude_paths = exclude_paths or {"/health", "/metrics", "/favicon.ico"}
    
#     async def dispatch(self, request: Request, call_next):
#         # Generate a unique ID for the request (check for existing correlation ID first)
#         request_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
#         # Add the request ID to the request's state
#         request.state.request_id = request_id
        
#         # Skip detailed logging for excluded paths
#         should_log = request.url.path not in self.exclude_paths
        
#         if should_log:
#             # Check request size and log warning if too large
#             content_length = request.headers.get("content-length")
#             if content_length and int(content_length) > getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024):  # 10MB default
#                 logger.warning(
#                     "Large request detected",
#                     extra={
#                         "request_id": request_id,
#                         "content_length": content_length,
#                         "path": request.url.path
#                     }
#                 )
        
#         start_time = time.time()
        
#         try:
#             if should_log:
#                 # Log the incoming request with structured data
#                 logger.info(
#                     "Incoming request",
#                     extra={
#                         "request_id": request_id,
#                         "client_ip": self._get_client_ip(request),
#                         "method": request.method,
#                         "path": request.url.path,
#                         "query_params": str(request.query_params) if request.query_params else None,
#                         "user_agent": request.headers.get("user-agent", "unknown"),
#                         "content_type": request.headers.get("content-type"),
#                         "content_length": request.headers.get("content-length"),
#                         "timestamp": datetime.utcnow().isoformat()
#                     }
#                 )
            
#             # Call the actual endpoint
#             response = await call_next(request)
            
#             # Calculate processing time
#             process_time = (time.time() - start_time) * 1000  # in milliseconds
            
#             # Add the request ID to the response headers
#             response.headers["X-Request-ID"] = request_id
            
#             if should_log:
#                 # Log the completed response
#                 logger.info(
#                     "Request completed",
#                     extra={
#                         "request_id": request_id,
#                         "status_code": response.status_code,
#                         "process_time_ms": round(process_time, 2),
#                         "response_size": response.headers.get("content-length", "unknown"),
#                         "timestamp": datetime.utcnow().isoformat()
#                     }
#                 )
            
#             return response
            
#         except Exception as exc:
#             process_time = (time.time() - start_time) * 1000
            
#             # Log the exception with full context
#             logger.error(
#                 "Request failed with exception",
#                 extra={
#                     "request_id": request_id,
#                     "exception": str(exc),
#                     "exception_type": type(exc).__name__,
#                     "process_time_ms": round(process_time, 2),
#                     "path": request.url.path,
#                     "method": request.method,
#                     "client_ip": self._get_client_ip(request),
#                     "timestamp": datetime.utcnow().isoformat()
#                 },
#                 exc_info=True
#             )
            
#             # Return a structured error response
#             return JSONResponse(
#                 status_code=500,
#                 content={
#                     "error": "Internal Server Error",
#                     "message": "An unexpected error occurred while processing your request",
#                     "request_id": request_id,
#                     "timestamp": datetime.utcnow().isoformat(),
#                     "path": request.url.path
#                 },
#                 headers={"X-Request-ID": request_id}
#             )
    
#     def _get_client_ip(self, request: Request) -> str:
#         """Extract client IP considering proxy headers"""
#         # Check for forwarded headers first (common in production behind reverse proxies)
#         forwarded_for = request.headers.get("X-Forwarded-For")
#         if forwarded_for:
#             # Take the first IP in the chain
#             return forwarded_for.split(",")[0].strip()
        
#         real_ip = request.headers.get("X-Real-IP")
#         if real_ip:
#             return real_ip.strip()
        
#         # Fallback to direct client IP
#         return request.client.host if request.client else "unknown"


# class SecurityHeadersMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware to add security headers to all responses
#     """
    
#     async def dispatch(self, request: Request, call_next):
#         response = await call_next(request)
        
#         # Add security headers
#         security_headers = {
#             "X-Content-Type-Options": "nosniff",
#             "X-Frame-Options": "DENY",
#             "X-XSS-Protection": "1; mode=block",
#             "Referrer-Policy": "strict-origin-when-cross-origin",
#             "X-Permitted-Cross-Domain-Policies": "none"
#         }
        
#         # Add HSTS only for HTTPS
#         if request.url.scheme == "https":
#             security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
#         # Add Content Security Policy for HTML responses
#         content_type = response.headers.get("content-type", "")
#         if "text/html" in content_type:
#             security_headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
#         # Apply all security headers
#         for header, value in security_headers.items():
#             response.headers[header] = value
        
#         return response


# class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware to limit request payload size
#     """
    
#     def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
#         super().__init__(app)
#         self.max_size = max_size
    
#     async def dispatch(self, request: Request, call_next):
#         content_length = request.headers.get("content-length")
        
#         if content_length and int(content_length) > self.max_size:
#             return JSONResponse(
#                 status_code=413,
#                 content={
#                     "error": "Payload Too Large",
#                     "message": f"Request payload exceeds maximum size of {self.max_size} bytes",
#                     "max_size": self.max_size,
#                     "received_size": int(content_length)
#                 }
#             )
        
#         return await call_next(request)


# def register_middlewares(app: FastAPI):
#     """
#     Registers all middlewares for the FastAPI application.
#     The order of middleware is important - they are executed in reverse order of registration.
#     """
    
#     # Validate and prepare configuration
#     allowed_hosts = _get_allowed_hosts()
#     cors_origins = _get_cors_origins()
    
#     # 1. Request Size Limit Middleware (should be early to reject large requests quickly)
#     max_request_size = getattr(settings, 'MAX_REQUEST_SIZE', 10 * 1024 * 1024)  # 10MB default
#     app.add_middleware(RequestSizeLimitMiddleware, max_size=max_request_size)
    
#     # 2. GZip Middleware (compress responses) - should be high up
#     app.add_middleware(GZipMiddleware, minimum_size=1000)

#     # 3. Security Headers Middleware
#     app.add_middleware(SecurityHeadersMiddleware)

#     # 4. Trusted Host Middleware (protect against host header attacks)
#     if allowed_hosts and "*" not in allowed_hosts:
#         app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
#     else:
#         logger.warning("TrustedHostMiddleware disabled: ALLOWED_HOSTS contains '*' or is not configured")

#     # 5. CORS Middleware (allow cross-origin requests)
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=cors_origins,
#         allow_credentials=True,
#         allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
#         allow_headers=["*"],
#         expose_headers=["X-Request-ID"],  # Expose our custom header
#     )

#     # 6. Custom logging middleware (should be last to capture all request/response data)
#     exclude_paths = getattr(settings, 'LOGGING_EXCLUDE_PATHS', {"/health", "/metrics", "/favicon.ico"})
#     app.add_middleware(ProfessionalLoggingMiddleware, exclude_paths=exclude_paths)
    
#     logger.info("All middlewares registered successfully")


# def _get_allowed_hosts() -> list[str]:
#     """Validate and return allowed hosts configuration"""
#     if not hasattr(settings, 'ALLOWED_HOSTS') or not settings.ALLOWED_HOSTS:
#         logger.warning("ALLOWED_HOSTS not configured, using restrictive default")
#         return ["localhost", "127.0.0.1"]
    
#     hosts = [host.strip() for host in settings.ALLOWED_HOSTS.split(",") if host.strip()]
    
#     if not hosts:
#         logger.warning("ALLOWED_HOSTS is empty after parsing, using restrictive default")
#         return ["localhost", "127.0.0.1"]
    
#     logger.info(f"Configured allowed hosts: {hosts}")
#     return hosts


# def _get_cors_origins() -> list[str]:
#     """Validate and return CORS origins configuration"""
#     if not hasattr(settings, 'CORS_ORIGINS') or not settings.CORS_ORIGINS:
#         logger.warning("CORS_ORIGINS not configured, using restrictive default")
#         return ["http://localhost:3000", "http://localhost:8000"]
    
#     origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    
#     if not origins:
#         logger.warning("CORS_ORIGINS is empty after parsing, using restrictive default")
#         return ["http://localhost:3000", "http://localhost:8000"]
    
#     logger.info(f"Configured CORS origins: {origins}")
#     return origins


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

from fastapi import FastAPI
from app.api.v1.endpoints import (
    book,
    auth,
    user,
    review,
    tag,
)
from app.core.config import settings
from app.core.exceptions import AppException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.core.middleware import register_middlewares
# --- App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_V1_STR,
    description="A modern API for managing a book collection.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# --- Include Exception Handler ---
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

register_middlewares(app)

# --- Include Routers ---
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(user.router)
app.include_router(review.router)
app.include_router(tag.router)


# --- Root Endpoint (Health Check) ---
@app.get("/", tags=["Health Check"])
async def root():
    """
    Root endpoint for health check.
    """
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME}"}


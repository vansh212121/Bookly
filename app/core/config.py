from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Set
from typing import ClassVar

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bookly API"
    API_V1_STR: str = "/api/v1"

    # --- Database & JWT Secrets ---
    DATABASE_URL: str
    JWT_SECRET: str

    # --- Token Lifespans ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # --- Redis Configuration ---
    REDIS_URL: str
    
    # These tell Celery where to find the message queue and where to store results.
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # This is a good production setting for Celery.
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True
    

    # --- Middleware Configuration ---

    ALLOWED_HOSTS: str
    CORS_ORIGINS: str

    # These are optional settings with good defaults
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOGGING_EXCLUDE_PATHS: Set[str] = {
        "/health",
        "/metrics",
        "/favicon.ico",
        "/docs",
        "/openapi.json",
    }

    # Mail Config
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_DEBUG: bool = False
    

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

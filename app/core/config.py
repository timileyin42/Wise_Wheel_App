"""
Application configuration settings with enhanced security and validation.
Loads from environment variables with type checking.
"""

from pathlib import Path
from pydantic import AnyUrl, PostgresDsn, RedisDsn, validator, EmailStr
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Application Metadata
    PROJECT_TITLE: str = "WiseWheel"
    PROJECT_DESCRIPTION: str = "Backend API for WiseWheel car renting web app for renting, booking of cars"
    PROJECT_VERSION: str = "1.0.0"
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"

    # Database
    POSTGRES_URL: PostgresDsn
    TEST_DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_CA: str

    # Auth
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google OAuth2


    GOOGLE_REDIRECT_URI: str
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None

    # Mailjet
    MAILJET_API_KEY: Optional[str] = None
    MAILJET_API_SECRET: Optional[str] = None
    MAILJET_SENDER_EMAIL: EmailStr = "noreply@wisewheels.com"
    MAILJET_SENDER_NAME: str = "WiseWheels Auto Rentals"
    DEFAULT_FROM_EMAIL: EmailStr = "noreply@wisewheels.com"

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # Paystack
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYSTACK_BASE_URL: Optional[str] = None

    # Redis (for rate limiting)
    # REDIS_URL: Optional[RedisDsn] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    FRONTEND_URL: str

    CORS_ORIGINS: List[str] = ["*"]

    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"

settings = Settings()

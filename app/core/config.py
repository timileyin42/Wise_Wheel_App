"""
Application configuration settings with enhanced security and validation.
Loads from environment variables with type checking using Pydantic.
"""

import json
from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, AnyUrl, PostgresDsn, RedisDsn, EmailStr, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # === Project Metadata ===
    PROJECT_TITLE: str = "WiseWheel"
    PROJECT_DESCRIPTION: str = "Backend API for WiseWheel car renting web app for renting and booking of cars."
    PROJECT_VERSION: str = "1.0.0"
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"

    # === Database Configuration ===
    POSTGRES_URL: PostgresDsn
    TEST_DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_CA: str

    # === Authentication ===
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === Google Integration ===
    GOOGLE_REDIRECT_URI: str
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None

    # === Mailjet Integration ===
    MAILJET_API_KEY: Optional[str] = None
    MAILJET_API_SECRET: Optional[str] = None
    MAILJET_SENDER_EMAIL: EmailStr = "noreply@wisewheels.com"
    MAILJET_SENDER_NAME: str = "WiseWheels Auto Rentals"
    DEFAULT_FROM_EMAIL: EmailStr = "noreply@wisewheels.com"

    # === Cloudinary Configuration ===
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # === Paystack Payment Integration ===
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYSTACK_BASE_URL: Optional[str] = None

    # === CORS Configuration ===
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    FRONTEND_URL: str
    CORS_ORIGINS: List[str] = ["*"]

    # === App Environment ===
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """
        Ensures CORS origins can be parsed correctly from JSON-style or comma-separated strings in .env
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


settings = Settings()


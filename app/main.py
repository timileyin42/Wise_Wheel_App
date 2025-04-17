"""
Main application entry point for WiseWheels API
"""

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import engine, async_session
from app.db.base import Base
from app.core.config import settings
from app.api import (
    auth,
    cars,
    bookings,
    payments,
    users,
    admin
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with async database initialization"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    except SQLAlchemyError as e:
        raise RuntimeError(f"Database initialization failed: {str(e)}")
    finally:
        await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(cars.router, prefix="/api", tags=["Cars"])
app.include_router(bookings.router, prefix="/api", tags=["Bookings"])
app.include_router(payments.router, prefix="/api", tags=["Payments"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
async def health_check():
    """System health check endpoint"""
    try:
        # Test database connection
        async with async_session() as session:
            await session.execute("SELECT 1")
        return {"status": "healthy"}
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting WiseWheels API..")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="./key.pem",  # Add in production
        ssl_certfile="./cert.pem"  # Add in production
    )

"""
Main application entry point for WiseWheels API
"""

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import engine, async_session
from app.db.base import Base
from app.api import notifications
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

print("Starting WiseWheels API..")
print("CORS ORIGINS LOADED:", settings.BACKEND_CORS_ORIGINS)

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
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/", status_code=status.HTTP_200_OK, tags=["System"])
async def root():
    """Root endpoint to confirm the API is running"""
    return {"message": "WiseWheel API is running!"}

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

@app.get("/ping", status_code=status.HTTP_200_OK, tags=["System"])
async def ping():
    """Simple ping endpoint for external monitoring services"""
    import time
    return {"message": "pong", "timestamp": time.time()}

@app.get("/db-stats", status_code=status.HTTP_200_OK, tags=["System"])
async def database_stats():
    """Get database connection statistics and health metrics"""
    try:
        # Add current pool information
        pool_info = {}
        try:
            pool = engine.pool
            pool_info = {
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "checked_in": pool.checkedin()
            }
        except Exception as e:
            pool_info = {"error": f"Could not get pool info: {e}"}
        
        return {
            "pool_info": pool_info,
            "engine_info": {
                "url": str(engine.url).replace(engine.url.password or "", "***") if engine.url.password else str(engine.url),
                "echo": engine.echo
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving database stats: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

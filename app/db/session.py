from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Create engine without SSL
engine = create_async_engine(
    str(settings.POSTGRES_URL),
    echo=True,
    poolclass=NullPool,
    connect_args={
        "command_timeout": 60,
        "server_settings": {
            "application_name": "WiseWheel_App",
        }
    }
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db():
    """Database session generator"""
    async with async_session() as session:
        yield session


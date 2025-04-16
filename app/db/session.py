from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import ssl
import os

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CA_CERT_PATH = os.path.join(BASE_DIR, 'certs', 'ca.pem')

# Create SSL context
ssl_ctx = ssl.create_default_context(cafile=CA_CERT_PATH)
ssl_ctx.verify_mode = ssl.CERT_REQUIRED

# Create engine with explicit SSL configuration
engine = create_async_engine(
    str(settings.POSTGRES_URL),
    echo=True,
    connect_args={
        "ssl": ssl_ctx  # Only pass SSL context
    }
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

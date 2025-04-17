from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import ssl
import tempfile

# Write DATABASE_CA (from .env) to a temp file
def write_ca_cert_to_temp_file(ca_content: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w")
    temp_file.write(ca_content)
    temp_file.close()
    return temp_file.name

# Write cert to a temporary file
CA_CERT_PATH = write_ca_cert_to_temp_file(settings.DATABASE_CA)

# Create SSL context
ssl_ctx = ssl.create_default_context(cafile=CA_CERT_PATH)
ssl_ctx.verify_mode = ssl.CERT_REQUIRED

# Create engine with SSL
engine = create_async_engine(
    str(settings.POSTGRES_URL),
    echo=True,
    connect_args={
        "ssl": ssl_ctx
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


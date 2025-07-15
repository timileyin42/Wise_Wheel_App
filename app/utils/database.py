"""
Database utility functions for connection management and health monitoring
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import async_session, engine

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database connection manager with retry and keepalive functionality"""
    
    def __init__(self):
        self.is_connected = True
        self.last_ping = None
        
    async def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            async with async_session() as session:
                await session.execute("SELECT 1")
                self.is_connected = True
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            self.is_connected = False
            return False
    
    async def get_session_with_retry(self, max_retries: int = 3) -> AsyncSession:
        """Get database session with automatic retry logic"""
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                session = async_session()
                # Test the session
                await session.execute("SELECT 1")
                return session
            except Exception as e:
                logger.warning(f"Database session attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise SQLAlchemyError(f"Failed to get database session after {max_retries} attempts")
    
    async def execute_with_retry(self, query: str, params: Optional[dict] = None, max_retries: int = 3):
        """Execute query with automatic retry on connection failure"""
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with async_session() as session:
                    if params:
                        result = await session.execute(query, params)
                    else:
                        result = await session.execute(query)
                    await session.commit()
                    return result
            except Exception as e:
                logger.warning(f"Query execution attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise
    
    async def periodic_health_check(self, interval: int = 240):
        """Run periodic health checks every 4 minutes"""
        while True:
            try:
                await self.test_connection()
                if self.is_connected:
                    logger.info("Database periodic health check: OK")
                else:
                    logger.warning("Database periodic health check: FAILED")
            except Exception as e:
                logger.error(f"Error during periodic health check: {e}")
            
            await asyncio.sleep(interval)

# Global database manager instance
db_manager = DatabaseManager()

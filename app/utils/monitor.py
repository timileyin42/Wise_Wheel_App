"""
Database connection monitoring and management utilities
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from app.db.session import engine

logger = logging.getLogger(__name__)

class ConnectionMonitor:
    """Monitor database connections and provide insights"""
    
    def __init__(self):
        self.stats = {
            "total_connections": 0,
            "failed_connections": 0,
            "last_successful_connection": None,
            "last_failed_connection": None,
            "uptime_start": datetime.utcnow()
        }
    
    def record_success(self):
        """Record successful connection"""
        self.stats["total_connections"] += 1
        self.stats["last_successful_connection"] = datetime.utcnow()
    
    def record_failure(self, error: str):
        """Record failed connection"""
        self.stats["failed_connections"] += 1
        self.stats["last_failed_connection"] = datetime.utcnow()
        logger.warning(f"Database connection failed: {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        uptime = datetime.utcnow() - self.stats["uptime_start"]
        success_rate = 0
        if self.stats["total_connections"] > 0:
            success_rate = ((self.stats["total_connections"] - self.stats["failed_connections"]) 
                          / self.stats["total_connections"]) * 100
        
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "success_rate_percent": round(success_rate, 2),
            "pool_size": getattr(engine.pool, "size", "N/A"),
            "checked_out_connections": getattr(engine.pool, "checkedout", "N/A"),
        }
    
    async def log_pool_status(self):
        """Log current connection pool status"""
        try:
            pool = engine.pool
            logger.info(f"Connection Pool Status - Size: {pool.size()}, "
                       f"Checked out: {pool.checkedout()}, "
                       f"Overflow: {pool.overflow()}, "
                       f"Checked in: {pool.checkedin()}")
        except Exception as e:
            logger.error(f"Error getting pool status: {e}")

# Global connection monitor
connection_monitor = ConnectionMonitor()

async def periodic_connection_monitor():
    """Run periodic connection monitoring"""
    while True:
        try:
            await connection_monitor.log_pool_status()
            stats = connection_monitor.get_stats()
            logger.info(f"DB Stats - Total: {stats['total_connections']}, "
                       f"Failed: {stats['failed_connections']}, "
                       f"Success Rate: {stats['success_rate_percent']}%")
        except Exception as e:
            logger.error(f"Error in connection monitor: {e}")
        
        # Monitor every 5 minutes
        await asyncio.sleep(300)

from datetime import datetime, timezone
from typing import Optional

def to_utc_naive(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Convert timezone-aware datetime to UTC naive datetime.
    If datetime is already naive, return as-is.
    If datetime is None, return None.
    """
    if dt is None:
        return None
    
    if dt.tzinfo is not None:
        # Convert to UTC and remove timezone info
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.replace(tzinfo=None)
    
    return dt

def ensure_utc_naive(dt: datetime) -> datetime:
    """
    Ensure datetime is UTC naive.
    Raises ValueError if datetime is None.
    """
    if dt is None:
        raise ValueError("Datetime cannot be None")
    
    return to_utc_naive(dt)
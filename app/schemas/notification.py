from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

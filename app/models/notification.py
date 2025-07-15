from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import UUIDBase, TimestampMixin

class Notification(UUIDBase, TimestampMixin):
    __tablename__ = "notifications"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    # Optionally, you can add a type or link field
    # type = Column(String(50))
    # link = Column(String(255))

    user = relationship("User", back_populates="notifications")
    
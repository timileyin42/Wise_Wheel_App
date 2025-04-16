import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import UUIDBase, TimestampMixin
from sqlalchemy.orm import relationship

class User(UUIDBase, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")
    
    # OAuth2 fields
    google_id = Column(String(255), unique=True, index=True)
    profile_image = Column(String(512))  # Cloudinary URL
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    
    __table_args__ = (
        Index('ix_users_email_phone', 'email', 'phone'),
    )

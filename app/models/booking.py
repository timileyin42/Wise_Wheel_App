from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import UUIDBase, TimestampMixin
from sqlalchemy.orm import relationship

class Booking(UUIDBase, TimestampMixin):
    __tablename__ = "bookings"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    car_id = Column(UUID(as_uuid=True), ForeignKey("cars.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(Boolean, default=False)
    status = Column(String(20), default="pending")  #[pending, confirmed, cancelled]
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    car = relationship("Car", back_populates="bookings")
    
    __table_args__ = (
        Index('ix_bookings_user_status', 'user_id', 'status'),
        Index('ix_bookings_dates', start_date, end_date)
    )

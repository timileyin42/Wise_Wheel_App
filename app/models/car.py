from sqlalchemy import Column, String, Float, Boolean, Integer, JSON, Index
from geoalchemy2 import Geometry
from app.models.base import UUIDBase, TimestampMixin
from sqlalchemy.orm import relationship
from datetime import datetime

class Car(UUIDBase, TimestampMixin):
    __tablename__ = "cars"
    
    make = Column(String(100), index=True, nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    daily_rate = Column(Float, nullable=False)
    location = Column(Geometry(geometry_type='POINT', srid=4326))  # For Google Maps
    images = Column(JSON)  # Array of Cloudinary URLs
    is_available = Column(Boolean, default=True)
    
    # Relationships
    bookings = relationship("Booking", back_populates="car")
    
    __table_args__ = (
        Index('ix_cars_make_model', 'make', 'model'),
        Index('ix_cars_location', location, postgresql_using='gist')
    )

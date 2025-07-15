from pydantic import BaseModel, Field, field_validator, computed_field
from typing import List, Optional
from datetime import datetime
import uuid

class CarBase(BaseModel):
    """
    Base schema for car properties
    """
    make: str = Field(..., example="Toyota", max_length=100)
    model: str = Field(..., example="Camry", max_length=100)
    year: int = Field(..., example=2022, gt=1900, lt=2100)
    daily_rate: float = Field(..., example=50.0, gt=0)
    license_plate: str = Field(..., example="ABC123XYZ", max_length=20)
    latitude: Optional[float] = Field(None, example=6.5244, ge=-90, le=90)
    longitude: Optional[float] = Field(None, example=3.3792, ge=-180, le=180)

class CarCreate(CarBase):
    """
    Schema for creating new car entries (admin only)
    """
    pass

class CarResponse(BaseModel):
    """
    Schema for returning car data in API responses
    """
    id: str
    make: str
    model: str
    year: int
    daily_rate: float
    license_plate: str
    is_available: bool
    images: Optional[List[str]] = Field(
        default_factory=list,
        example=["https://res.cloudinary.com/.../car1.jpg"],
        description="List of Cloudinary image URLs"
    )
    created_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string"""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator('images', mode='before')
    @classmethod
    def handle_images(cls, v):
        """Handle images field"""
        if v is None:
            return []
        return v

    class Config:
        from_attributes = True

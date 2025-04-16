from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class CarBase(BaseModel):
    """
    Base schema for car properties
    """
    make: str = Field(..., example="Toyota", max_length=100)
    model: str = Field(..., example="Camry", max_length=100)
    year: int = Field(..., example=2022, gt=1900, lt=2100)
    daily_rate: float = Field(..., example=50.0, gt=0)
    license_plate: str = Field(..., example="ABC123XYZ", max_length=20)
    latitude: float = Field(..., example=6.5244, ge=-90, le=90)
    longitude: float = Field(..., example=3.3792, ge=-180, le=180)

class CarCreate(CarBase):
    """
    Schema for creating new car entries (admin only)
    """
    pass

class CarResponse(CarBase):
    """
    Schema for returning car data in API responses
    """
    id: str
    is_available: bool
    images: List[str] = Field(
        [],
        example=["https://res.cloudinary.com/.../car1.jpg"],
        description="List of Cloudinary image URLs"
    )
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            # Convert PostGIS geometry to GeoJSON
            "location": lambda v: {
                "type": "Point",
                "coordinates": [v.longitude, v.latitude]
            } if v else None
        }

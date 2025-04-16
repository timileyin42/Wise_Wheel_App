from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, ForwardRef

# Forward references to break circular dependencies
CarResponse = ForwardRef('CarResponse')
UserResponse = ForwardRef('UserResponse')

class BookingBase(BaseModel):
    """
    Base schema for booking properties
    """
    start_date: datetime = Field(
        ...,
        example="2023-12-01T09:00:00Z",
        description="Rental start date/time in UTC"
    )
    end_date: datetime = Field(
        ...,
        example="2023-12-05T17:00:00Z",
        description="Rental end date/time in UTC"
    )

    @validator('end_date')
    def validate_dates(cls, v, values):
        """Ensure end date is after start date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v

class BookingCreate(BookingBase):
    """
    Schema for creating new bookings
    """
    car_id: str = Field(
        ...,
        example="550e8400-e29b-41d4-a716-446655440000",
        description="UUID of the car being booked"
    )

class BookingResponse(BookingBase):
    """
    Schema for returning booking data in API responses
    """
    id: str
    total_amount: float
    payment_status: bool
    status: str
    created_at: datetime
    car: CarResponse
    user: UserResponse

    class Config:
        from_attributes = True

# Import the actual models after their definition
from app.schemas.car import CarResponse
from app.schemas.user import UserResponse

# Update forward references - CORRECTED for Pydantic v2
BookingResponse.model_rebuild()

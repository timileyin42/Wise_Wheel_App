from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, field_validator, model_validator
from typing import Optional, Any
import re
from uuid import UUID

class UserBase(BaseModel):
    """
    Base user schema containing common fields
    """
    email: EmailStr = Field(
        ...,
        example="user@example.com",
        description="Unique email address for authentication"
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=20,
        example="+2348123456789",
        description="Phone number in international format"
    )

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format using regex"""
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Invalid phone number format")
        return v

class UserCreate(UserBase):
    """
    Schema for user registration through email/password
    """
    password: str = Field(
        ...,
        min_length=8,
        example="strongpassword123",
        description="Password with minimum 8 characters"
    )

class UserGoogleCreate(BaseModel):
    """
    Schema for Google OAuth2 user registration
    """
    google_id: str = Field(..., description="Unique identifier from Google")
    email: EmailStr
    name: Optional[str] = Field(None, description="Full name from Google profile")
    picture: Optional[str] = Field(None, description="Profile picture URL from Google")

class UserUpdate(BaseModel):
    """
    Schema for updating user profile information
    """
    phone: Optional[str] = None
    profile_image: Optional[str] = Field(
        None,
        description="Cloudinary URL for profile picture"
    )

class UserResponse(UserBase):
    """
    Schema for returning user data in API responses
    """
    id: str = Field(..., description="UUID primary key")
    created_at: datetime
    is_verified: bool
    role: str
    profile_image: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def convert_uuid_fields(cls, data: Any) -> Any:
        """Convert UUID objects to strings before validation"""
        if isinstance(data, dict):
            if 'id' in data and isinstance(data['id'], UUID):
                data['id'] = str(data['id'])
        elif hasattr(data, 'id') and isinstance(data.id, UUID):
            data.id = str(data.id)
        return data

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "phone": "+2348123456789",
                "created_at": "2023-01-01T00:00:00Z",
                "is_verified": True,
                "role": "user",
                "profile_image": "https://res.cloudinary.com/.../profile.jpg"
            }
        }

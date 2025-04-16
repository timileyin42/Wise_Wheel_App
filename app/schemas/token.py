from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    """
    Schema for JWT authentication response
    """
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="JWT access token for API authorization"
    )
    token_type: str = Field(
        default="bearer",
        example="bearer",
        description="Token type (always 'bearer')"
    )

class TokenPayload(BaseModel):
    """
    Schema for decoded JWT token payload
    """
    sub: Optional[str] = None  # Subject (user email)
    exp: Optional[int] = None  # Expiration timestamp

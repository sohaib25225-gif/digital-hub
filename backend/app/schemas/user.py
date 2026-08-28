from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

from app.db.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user data in API responses (never includes password)."""
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schema for user data including hashed password (internal use only)."""
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)

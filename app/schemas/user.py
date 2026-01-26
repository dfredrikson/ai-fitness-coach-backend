"""
AI Fitness Coach - User Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    language: Optional[str] = None
    active_coach_id: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    language: str
    active_coach_id: Optional[str]
    strava_connected: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str
    exp: datetime

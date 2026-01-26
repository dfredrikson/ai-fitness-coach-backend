"""
AI Fitness Coach - Coach Schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CoachPersonalityBase(BaseModel):
    """Base coach personality schema."""
    name: str
    description: str
    icon: str


class CoachPersonalityResponse(CoachPersonalityBase):
    id: str
    style_params: dict
    is_default: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CoachPersonalityList(BaseModel):
    """List of coach personalities."""
    items: List[CoachPersonalityResponse]


class ChatMessage(BaseModel):
    """Schema for chat message."""
    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: str
    content: str
    is_from_user: bool
    message_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history."""
    messages: List[ChatMessageResponse]
    total: int


class CoachResponse(BaseModel):
    """Schema for coach AI response."""
    message: str
    coach_name: str
    coach_icon: str

"""
AI Fitness Coach - Activity Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ActivityBase(BaseModel):
    """Base activity schema."""
    type: str
    name: str
    start_date: datetime


class ActivityResponse(ActivityBase):
    """Schema for activity response."""
    id: str
    strava_id: Optional[int]
    distance_meters: float
    duration_seconds: int
    avg_pace: Optional[float]
    max_pace: Optional[float]
    avg_heartrate: Optional[int]
    max_heartrate: Optional[int]
    elevation_gain: float
    calories: Optional[int]
    analyzed: bool
    synced_at: datetime
    
    # Computed fields
    distance_km: float
    duration_minutes: float
    
    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for paginated activity list."""
    items: List[ActivityResponse]
    total: int
    page: int
    page_size: int


class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis response."""
    id: str
    activity_id: str
    coach_personality_id: str
    technical_analysis: Optional[str]
    corrections: Optional[str]
    motivation: Optional[str]
    metrics_summary: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityWithAnalysis(ActivityResponse):
    """Activity response with analysis included."""
    analyses: List[AIAnalysisResponse] = []

"""
AI Fitness Coach - Routine Schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RoutineDayBase(BaseModel):
    """Base routine day schema."""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    activity_type: str
    target_distance: Optional[float] = None  # km
    target_duration: Optional[int] = None  # minutes
    notes: Optional[str] = None


class RoutineDayCreate(RoutineDayBase):
    """Schema for creating a routine day."""
    pass


class RoutineDayResponse(RoutineDayBase):
    """Schema for routine day response."""
    id: str
    day_name: str
    
    class Config:
        from_attributes = True


class RoutineBase(BaseModel):
    """Base routine schema."""
    name: str = Field(..., min_length=1, max_length=255)


class RoutineCreate(RoutineBase):
    """Schema for creating a routine."""
    days: List[RoutineDayCreate] = []


class RoutineUpdate(BaseModel):
    """Schema for updating a routine."""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    days: Optional[List[RoutineDayCreate]] = None


class RoutineResponse(RoutineBase):
    """Schema for routine response."""
    id: str
    is_active: bool
    days: List[RoutineDayResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoutineListResponse(BaseModel):
    """List of routines."""
    items: List[RoutineResponse]


class RoutineComplianceDay(BaseModel):
    """Compliance for a single day."""
    day_of_week: int
    day_name: str
    expected: RoutineDayResponse
    completed: bool
    actual_activity: Optional[dict] = None


class RoutineComplianceResponse(BaseModel):
    """Weekly routine compliance report."""
    routine_id: str
    routine_name: str
    week_start: datetime
    days: List[RoutineComplianceDay]
    completion_rate: float  # percentage

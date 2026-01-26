"""Schemas module initialization."""
from app.schemas.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse, 
    Token, TokenPayload
)
from app.schemas.activity import (
    ActivityBase, ActivityResponse, ActivityListResponse,
    AIAnalysisResponse, ActivityWithAnalysis
)
from app.schemas.coach import (
    CoachPersonalityResponse, CoachPersonalityList,
    ChatMessage, ChatMessageResponse, ChatHistoryResponse, CoachResponse
)
from app.schemas.routine import (
    RoutineDayCreate, RoutineDayResponse,
    RoutineCreate, RoutineUpdate, RoutineResponse, RoutineListResponse,
    RoutineComplianceResponse
)

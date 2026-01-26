"""
AI Fitness Coach - Coach Personality Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.sqlite import TEXT
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class CoachPersonality(Base):
    """Coach personality model for storing AI coach profiles."""
    __tablename__ = "coach_personalities"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    icon = Column(String(10), nullable=False)
    
    # AI configuration
    system_prompt = Column(TEXT, nullable=False)
    style_params = Column(JSON, default=dict)
    
    # Status
    is_default = Column(Boolean, default=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CoachPersonality {self.name}>"

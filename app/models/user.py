"""
AI Fitness Coach - User Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Strava integration
    strava_athlete_id = Column(String(50), unique=True, nullable=True)
    strava_access_token = Column(TEXT, nullable=True)
    strava_refresh_token = Column(TEXT, nullable=True)
    strava_token_expires = Column(DateTime, nullable=True)
    
    # Coach preference
    active_coach_id = Column(String(36), ForeignKey("coach_personalities.id"), nullable=True)
    
    # Settings
    language = Column(String(10), default="es")
    preferences = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    routines = relationship("Routine", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    active_coach = relationship("CoachPersonality", foreign_keys=[active_coach_id])
    
    def is_strava_connected(self) -> bool:
        """Check if user has connected Strava account."""
        return self.strava_access_token is not None
    
    def __repr__(self):
        return f"<User {self.email}>"

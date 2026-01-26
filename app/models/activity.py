"""
AI Fitness Coach - Activity Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Activity(Base):
    """Activity model for storing Strava activities."""
    __tablename__ = "activities"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Strava data
    strava_id = Column(BigInteger, unique=True, index=True)
    type = Column(String(50))  # Run, Ride, Swim, etc.
    name = Column(String(255))
    start_date = Column(DateTime)
    
    # Metrics
    distance_meters = Column(Float, default=0)
    duration_seconds = Column(Integer, default=0)
    avg_pace = Column(Float, nullable=True)  # min/km
    max_pace = Column(Float, nullable=True)
    avg_heartrate = Column(Integer, nullable=True)
    max_heartrate = Column(Integer, nullable=True)
    elevation_gain = Column(Float, default=0)
    calories = Column(Integer, nullable=True)
    
    # Raw data from Strava
    raw_data = Column(JSON, default=dict)
    
    # Analysis status
    analyzed = Column(Boolean, default=False)
    
    # Timestamps
    synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    analyses = relationship("AIAnalysis", back_populates="activity", cascade="all, delete-orphan")
    
    @property
    def distance_km(self) -> float:
        """Get distance in kilometers."""
        return self.distance_meters / 1000 if self.distance_meters else 0
    
    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration_seconds / 60 if self.duration_seconds else 0
    
    def __repr__(self):
        return f"<Activity {self.name} ({self.type})>"


class AIAnalysis(Base):
    """AI Analysis for activities."""
    __tablename__ = "ai_analyses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    activity_id = Column(String(36), ForeignKey("activities.id"), nullable=False)
    coach_personality_id = Column(String(36), ForeignKey("coach_personalities.id"), nullable=False)
    
    # Analysis content
    technical_analysis = Column(String, nullable=True)
    corrections = Column(String, nullable=True)
    motivation = Column(String, nullable=True)
    metrics_summary = Column(JSON, default=dict)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    activity = relationship("Activity", back_populates="analyses")
    coach_personality = relationship("CoachPersonality")
    
    def __repr__(self):
        return f"<AIAnalysis for Activity {self.activity_id}>"

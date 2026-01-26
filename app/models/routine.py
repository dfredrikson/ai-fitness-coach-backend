"""
AI Fitness Coach - Routine Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Routine(Base):
    """Routine model for weekly training plans."""
    __tablename__ = "routines"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="routines")
    days = relationship("RoutineDay", back_populates="routine", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Routine {self.name}>"


class RoutineDay(Base):
    """Routine day model for specific day training targets."""
    __tablename__ = "routine_days"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    routine_id = Column(String(36), ForeignKey("routines.id"), nullable=False)
    
    # Day configuration (0=Monday, 6=Sunday)
    day_of_week = Column(Integer, nullable=False)
    activity_type = Column(String(50), nullable=False)  # Run, Ride, etc.
    target_distance = Column(Float, nullable=True)  # km
    target_duration = Column(Integer, nullable=True)  # minutes
    notes = Column(String(500), nullable=True)
    
    # Relationship
    routine = relationship("Routine", back_populates="days")
    
    @property
    def day_name(self) -> str:
        """Get day name in Spanish."""
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return days[self.day_of_week] if 0 <= self.day_of_week <= 6 else "Desconocido"
    
    def __repr__(self):
        return f"<RoutineDay {self.day_name} - {self.activity_type}>"

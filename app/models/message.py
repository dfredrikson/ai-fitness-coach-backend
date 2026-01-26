"""
AI Fitness Coach - Message Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Message(Base):
    """Message model for chat history."""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    activity_id = Column(String(36), ForeignKey("activities.id"), nullable=True)
    
    # Message content
    message_type = Column(String(50), default="chat")  # chat, analysis, reminder, motivation
    content = Column(TEXT, nullable=False)
    is_from_user = Column(Boolean, default=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="messages")
    
    def __repr__(self):
        role = "User" if self.is_from_user else "Coach"
        return f"<Message from {role}>"

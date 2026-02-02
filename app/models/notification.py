"""
AI Fitness Coach - Notification Model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Notification(Base):
    """Notification model for storing in-app and push notifications."""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Content
    type = Column(String(50), nullable=False)  # activity_motivation, routine_reminder, etc.
    title = Column(String(255), nullable=False)
    body = Column(String, nullable=False)
    data = Column(JSON, default=dict)  # Metadata like activity_id, url, etc.
    
    # Status
    is_read = Column(Boolean, default=False)
    sent_via_push = Column(Boolean, default=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<Notification {self.type} for {self.user_id}>"

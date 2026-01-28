from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class ActivityMotivation(Base):
    __tablename__ = "activity_motivations"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, index=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

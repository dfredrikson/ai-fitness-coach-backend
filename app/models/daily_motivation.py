from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class DailyMotivation(Base):
    __tablename__ = "daily_motivations"

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    date = Column(Date, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

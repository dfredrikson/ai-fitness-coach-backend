from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.motivation import (
    get_daily_motivation,
    get_latest_activity_motivation
)

router = APIRouter(prefix="/motivation", tags=["Motivation"])

@router.get("/daily")
def daily(db: Session = Depends(get_db)):
    return get_daily_motivation(db)

@router.get("/latest-activity")
def latest_activity(db: Session = Depends(get_db)):
    return get_latest_activity_motivation(db)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models import ActivityMotivation

from app.core.database import get_db
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

@router.get("/random-activity")
def random_activity_message(db: Session = Depends(get_db)):
    msg = db.query(ActivityMotivation).order_by(func.random()).first()

    if not msg:
        return {"message": "🔥 Nueva actividad registrada. Seguimos sumando."}

    return {"message": msg.message}

@router.post("/seed-activity")
def seed_activity_messages(db: Session = Depends(get_db)):
    messages = [
        "🔥 Sumaste otra. El hábito gana.",
        "💪 Nadie entrena motivado siempre. Vos entrenás igual.",
        "🚀 Una más. Estás construyendo disciplina.",
        "🏃 Cada sesión te hace más fuerte.",
        "🧠 Constancia > Excusas.",
    ]

    for m in messages:
        db.add(ActivityMotivation(message=m))

    db.commit()

    return {"status": "ok", "count": len(messages)}


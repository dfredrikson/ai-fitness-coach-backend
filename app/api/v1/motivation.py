from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import DailyMotivation, ActivityMotivation

router = APIRouter(prefix="/motivation", tags=["Motivation"])

@router.get("/daily")
def fetch_daily_motivation(db: Session = Depends(get_db)):
    msg = db.query(DailyMotivation)\
        .order_by(DailyMotivation.date.desc())\
        .first()

    if not msg:
        return {"message": None}

    return {"message": msg.message}

@router.get("/latest-activity")
def get_latest_activity_motivation(db: Session = Depends(get_db)):
    msg = db.query(ActivityMotivation)\
        .order_by(ActivityMotivation.created_at.desc())\
        .first()

    if not msg:
        return {"message": None}

    return {"message": msg.message}

#temporal script for testing ///////////////////////////////////////////

from datetime import datetime, date

@router.post("/seed")
def seed_motivations(db: Session = Depends(get_db)):

    daily_messages = [
        "Hoy es un gran día para entrenar 💪",
        "La constancia vence a la motivación.",
        "Paso a paso, progreso asegurado.",
        "Aunque cueste, seguí. Vale la pena.",
        "Tu yo del futuro te va a agradecer esto."
    ]

    activity_messages = [
        "Excelente trabajo 💥 Seguimos así!",
        "Me encanta tu constancia 🔥",
        "Vamos que se puede 💪 Gran sesión.",
        "Cada entrenamiento suma 🏃‍♂️",
        "Orgulloso de tu disciplina 👏"
    ]

    # Insert daily if empty
    if db.query(DailyMotivation).count() == 0:
        for msg in daily_messages:
            db.add(DailyMotivation(message=msg, date=date.today()))

    # Insert activity if empty
    if db.query(ActivityMotivation).count() == 0:
        for msg in activity_messages:
            db.add(ActivityMotivation(message=msg, created_at=datetime.utcnow()))

    db.commit()

    return {"status": "ok", "message": "Seed completed"}

import random
from datetime import date
from app.models.daily_motivation import DailyMotivation
from app.core.database import SessionLocal

MESSAGES = [
    "💪 Hoy es un gran día para entrenar",
    "🔥 La constancia vence a la motivación",
    "🏃‍♂️ Un pequeño esfuerzo hoy suma mañana",
    "✨ Cada día cuenta, seguí así",
    "🚀 Paso a paso se llega lejos"
]

def create_daily_motivation():
    db = SessionLocal()
    today = date.today()

    exists = db.query(DailyMotivation)\
        .filter(DailyMotivation.date == today)\
        .first()

    if exists:
        db.close()
        return

    message = random.choice(MESSAGES)

    motivation = DailyMotivation(
        message=message,
        date=today
    )

    db.add(motivation)
    db.commit()
    db.close()

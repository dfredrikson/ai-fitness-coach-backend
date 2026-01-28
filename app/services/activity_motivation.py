import random
from app.models.activity_motivation import ActivityMotivation
from app.core.database import SessionLocal

MESSAGES = [
    "👏 Excelente trabajo, seguí así",
    "🔥 Muy bien hecho, la constancia suma",
    "🏃‍♂️ Entrenamiento registrado, gran paso",
    "💪 Cada sesión cuenta, buen trabajo",
    "✨ Seguí así, vas muy bien"
]

def create_activity_motivation(activity_id: int):
    db = SessionLocal()

    message = random.choice(MESSAGES)

    motivation = ActivityMotivation(
        activity_id=activity_id,
        message=message
    )

    db.add(motivation)
    db.commit()
    db.close()

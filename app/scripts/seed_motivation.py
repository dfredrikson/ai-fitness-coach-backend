from app.core.database import SessionLocal
from app.models import DailyMotivation, ActivityMotivation
from datetime import datetime, date

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

db = SessionLocal()

# Insert daily messages
for msg in daily_messages:
    db.add(DailyMotivation(
        message=msg,
        date=date.today()
    ))

# Insert activity messages
for msg in activity_messages:
    db.add(ActivityMotivation(
        message=msg,
        created_at=datetime.utcnow()
    ))

db.commit()
db.close()

print("Motivation seeded successfully!")

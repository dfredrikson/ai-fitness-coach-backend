from app.core.database import SessionLocal
from app.models.coach_personality import CoachPersonality
from app.data.coach_personalities import COACH_PERSONALITIES
from datetime import datetime

db = SessionLocal()

for p in COACH_PERSONALITIES:
    exists = db.query(CoachPersonality).filter_by(id=p["id"]).first()
    if exists:
        continue

    coach = CoachPersonality(
        id=p["id"],
        name=p["name"],
        description=p["description"],
        icon=p["icon"],
        system_prompt=p["system_prompt"],
        style_params=p["style_params"],
        is_default=p["is_default"],
        created_at=datetime.utcnow()
    )
    db.add(coach)

db.commit()
db.close()

print("Coaches cargados correctamente ✅")

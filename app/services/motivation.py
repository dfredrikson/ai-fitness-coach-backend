from datetime import date
from sqlalchemy.orm import Session

from app.models.daily_motivation import DailyMotivation
from app.models.activity_motivation import ActivityMotivation

DEFAULT_MESSAGES = [
    "Disciplina > motivación. Entrená igual.",
    "Hecho hoy > perfecto mañana.",
    "Nadie entrena motivado. Entrená comprometido.",
    "El progreso ama la constancia.",
]

def get_daily_motivation(db: Session):
    today = date.today()

    row = db.query(DailyMotivation).filter_by(date=today).first()

    if row:
        return {"message": row.message}

    import random
    message = random.choice(DEFAULT_MESSAGES)

    new_row = DailyMotivation(message=message, date=today)
    db.add(new_row)
    db.commit()

    return {"message": message}


def get_latest_activity_motivation(db: Session):
    row = (
        db.query(ActivityMotivation)
        .order_by(ActivityMotivation.created_at.desc())
        .first()
    )

    if not row:
        return {"message": "Arranquemos. El primer paso es hoy."}

    return {"message": row.message}

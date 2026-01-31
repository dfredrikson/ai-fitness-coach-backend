from datetime import date
from sqlalchemy.orm import Session

from app.models.daily_motivation import DailyMotivation
from app.models.activity_motivation import ActivityMotivation

DEFAULT_MESSAGES = [
    "Un pequeño paso hoy cambia tu mañana.",
    "La constancia crea resultados.",
    "Avanzar lento también es avanzar.",
    "Elegí progreso, no perfección.",
    "Hoy cuenta. Hacelo valer.",
    "Disciplina antes que excusas.",
    "Tu futuro empieza hoy.",
    "Menos excusas, más acción.",
    "Hacelo simple. Hacelo posible.",
    "Un día a la vez.",
    "La acción vence a la duda.",
    "Seguir es ganar.",
    "Cada día suma.",
    "El hábito es poder.",
    "Constancia supera talento.",
    "Hoy es un buen día para empezar.",
    "Elegí moverte. Elegí crecer.",
    "Progreso real, todos los días.",
    "Pequeños esfuerzos, grandes cambios.",
    "Lo importante es no parar.",
    "Hoy podés un poco más.",
    "Tu mejor versión se construye.",
    "Menos pensar, más hacer.",
    "El cambio empieza con acción.",
    "Hacelo por vos.",
    "Avanzá, aunque sea poco.",
    "Cada decisión cuenta.",
    "El esfuerzo siempre vuelve.",
    "Hoy construís tu disciplina.",
    "Seguí. Estás en camino."
     
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

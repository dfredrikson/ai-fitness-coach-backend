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
    "Hoy elegiste cuidarte. Eso ya es una victoria enorme. Seguí así.",
    "Cada paso que das es una prueba de tu compromiso con vos mismo. Orgullo total.",
    "No es solo ejercicio: es amor propio en acción. Excelente trabajo.",
    "Cada vez que entrenás, le estás diciendo “sí” a tu futuro.",
    "Lo estás haciendo mejor de lo que creés. Seguí confiando en vos.",
    "Este esfuerzo es una inversión en tu bienestar. Vale la pena.",
    "Hoy sumaste salud, fuerza y amor propio. Gran trabajo.",
    "Aunque no lo notes, hoy creciste un poco más.",
    "Tu constancia es más poderosa que cualquier excusa.",
    "No es solo progreso físico: también es fortaleza mental.",
    "Cada entrenamiento es una promesa cumplida con vos mismo.",
    "Estás construyendo hábitos que te van a cambiar la vida.",
    "Aplaudite: no todos eligen superarse como vos.",
    "Hoy elegiste no rendirte. Eso es enorme.",
    "Paso a paso, te estás convirtiendo en quien querés ser.",
    "No importa la velocidad, importa que seguiste avanzando.",
    "Lo que hiciste hoy cuenta. Y mucho.",
    "Estás demostrando que podés más de lo que pensabas.",
    "Este es el tipo de esfuerzo que transforma.",
    "Cada gota de sudor es un acto de amor propio.",
    "Te estás regalando salud, energía y confianza.",
    "Aunque sea un día difícil, hoy ganaste una batalla.",
    "Seguir adelante, incluso cansado, habla de tu grandeza.",
    "Tu compromiso inspira. Seguí así.",
    "Hoy elegiste crecer. Mañana vas a agradecerlo.",
    "No es perfección, es progreso. Y vos estás progresando.",
    "Cada esfuerzo suma. Nada de esto es en vano.",
    "Te estás demostrando que sí podés.",
    "Tu disciplina de hoy es tu orgullo de mañana.",
    "Gracias por no rendirte con vos mismo. Excelente trabajo."
]

db = SessionLocal()

# Insert daily messages
# for msg in daily_messages:
#     db.add(DailyMotivation(
#         message=msg,
#         date=date.today()
#     ))

# Insert activity messages
for msg in activity_messages:
    db.add(ActivityMotivation(
        message=msg,
        created_at=datetime.utcnow()
    ))

db.commit()
db.close()

print("Motivation seeded successfully!")

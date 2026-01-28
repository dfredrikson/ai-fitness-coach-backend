from apscheduler.schedulers.background import BackgroundScheduler
from app.services.daily_motivation import create_daily_motivation

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        create_daily_motivation,
        trigger="cron",
        hour="8,12,16,20"
    )

    scheduler.start()



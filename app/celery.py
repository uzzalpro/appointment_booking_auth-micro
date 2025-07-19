
from app.config import config
from celery import Celery
from celery.schedules import crontab

def create_celery_app():
    celery_app = Celery("user_auth_service")
    
    # Load broker and redbeat config
    celery_app.config_from_object(config.CELERY)

    # Set timezone
    celery_app.conf.timezone = 'Asia/Dhaka'

    # Periodic task schedules
    celery_app.conf.beat_schedule = {
        "send-daily-reminders": {
        "task": "app.services.reminder.send_daily_appointment_reminders",
        # "schedule": crontab(hour=8, minute=0),
        'schedule': crontab(minute='*'), 
        },
        "generate-monthly-reports": {
            "task": "app.services.reports.generate_monthly_report",
            "schedule": crontab(day_of_month="1", hour=2, minute=0),  # 1st of every month at 2 AM
        },
    }

    return celery_app

celery_app = create_celery_app()


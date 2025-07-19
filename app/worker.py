from app.celery import celery_app

# Import tasks to register them with celery
import app.services.reminder
import app.services.reports_service


# from app import start_application

# app = start_application()

# celery_app = app.extensions["celery"]

# # Example beat schedule
# celery_app.conf.beat_schedule = {
#     "monthly-doctor-report": {
#         "task": "app.tasks.reports.generate_monthly_doctor_report",
#         "schedule": 60.0 * 60 * 24 * 30  # Every ~30 days
#     },
#     "daily-reminder-task": {
#         "task": "app.tasks.reminders.send_daily_reminders",
#         "schedule": 60.0 * 60 * 24  # Every day
#     },
# }


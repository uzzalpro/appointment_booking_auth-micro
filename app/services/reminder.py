from app.db.session import get_db
from app.db.models.models import Appointment, UserModel, AppointmentStatus
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.worker import celery_app
import pytz
from zoneinfo import ZoneInfo
from fastapi import Depends, Query


@celery_app.task(name="app.services.reminder.send_daily_appointment_reminders")
def send_daily_appointment_reminders():
    db = next(get_db())


    try:
        now = datetime.now(ZoneInfo("Asia/Dhaka"))
        target_time = now + timedelta(days=1)
        start = target_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end = target_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        appointments = db.query(Appointment).filter(
            Appointment.appointment_date >= start,
            Appointment.appointment_date <= end,
            Appointment.status == AppointmentStatus.CONFIRMED.value
        ).all()

        for appt in appointments:
            patient = db.query(UserModel).filter(UserModel.id == appt.patient_id).first()
            doctor = db.query(UserModel).filter(UserModel.id == appt.doctor_id).first()

            if patient and patient.email:
                subject = "Appointment Reminder"
                message = (
                    f"Dear {patient.full_name},\n\n"
                    f"This is a reminder for your appointment with Dr. {doctor.full_name} on {appt.appointment_date.strftime('%Y-%m-%d %H:%M')}.\n"
                    "Please be on time.\n\nThanks!"
                )
                print(f"To: {patient.email}\nSubject: {subject}\nBody:\n{message}\n")
    finally:
        db.close()



# @celery_app.task
# def send_daily_appointment_reminders():
#     print("Running daily appointment reminders...")

#     db: Session = next(get_db())

#     dhaka_tz = pytz.timezone("Asia/Dhaka")
#     target_time = datetime.now(dhaka_tz) + timedelta(days=1)
#     day_start = target_time.replace(hour=0, minute=0, second=0, microsecond=0)
#     day_end = day_start + timedelta(days=1)

#     appointments = db.query(Appointment).filter(
#         Appointment.appointment_date >= day_start,
#         Appointment.appointment_date < day_end,
#         Appointment.status == AppointmentStatus.CONFIRMED.value
#     ).all()

#     for appt in appointments:
#         patient = db.query(UserModel).filter(UserModel.id == appt.patient_id).first()
#         if patient:
#             print(f"[Reminder] To: {patient.email} | Appointment at: {appt.appointment_date}")

#     db.close()
from app.db.session import get_db
from app.db.models.models import Appointment, UserModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.worker import celery_app
import pytz
from typing import Optional,List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.models import DoctorReport, AppointmentStatus

from sqlalchemy import func, extract,distinct


from sqlalchemy import distinct  # Add this import

from datetime import datetime
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from sqlalchemy.orm import joinedload

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from typing import List, Dict, Set
from collections import defaultdict

def generate_monthly_reports(db: Session, month: int, year: int) -> List[DoctorReport]:
    """
    Generate monthly reports by:
    1. Fetching all completed/confirmed appointments for the month
    2. Getting doctor fees from users table
    3. Calculating metrics per doctor
    """
    try:
        # 1. Check if reports already exist
        if db.query(DoctorReport).filter(
            DoctorReport.month == month,
            DoctorReport.year == year
        ).first():
            raise ValueError(f"Reports already exist for {month}/{year}")

        # 2. Get all appointments for the period
        appointments = db.query(Appointment).filter(
            extract('month', Appointment.appointment_date) == month,
            extract('year', Appointment.appointment_date) == year,
            Appointment.status.in_(['completed', 'confirmed'])
        ).all()

        if not appointments:
            raise HTTPException(404, f"No appointments found for {month}/{year}")

        # 3. Get all doctor IDs and fetch their fees in one query
        doctor_ids = {appt.doctor_id for appt in appointments}
        doctors = db.query(UserModel.id, UserModel.consultation_fee).filter(
            UserModel.id.in_(doctor_ids)
        ).all()
        
        doctor_fees = {doc.id: (doc.consultation_fee or 0) for doc in doctors}

        # 4. Calculate metrics
        doctor_metrics = defaultdict(lambda: {
            'appointments': 0,
            'patients': set(),
            'fee': 0
        })

        for appt in appointments:
            doctor_id = appt.doctor_id
            doctor_metrics[doctor_id]['appointments'] += 1
            doctor_metrics[doctor_id]['patients'].add(appt.patient_id)
            doctor_metrics[doctor_id]['fee'] = doctor_fees.get(doctor_id, 0)

        # 5. Create and save reports
        reports = []
        for doctor_id, metrics in doctor_metrics.items():
            report = DoctorReport(
                doctor_id=doctor_id,
                month=month,
                year=year,
                total_patient_visits=len(metrics['patients']),
                total_appointments=metrics['appointments'],
                total_earnings=float(metrics['appointments'] * metrics['fee'])
            )
            db.add(report)
            reports.append(report)

        db.commit()
        return reports

    except ValueError as e:
        db.rollback()
        raise HTTPException(400, str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Report generation failed: {str(e)}")
# @celery_app.task
# def generate_monthly_report():
#     print("Generating monthly doctor report...")

#     db: Session = next(get_db())
#     now = datetime.now(pytz.timezone("Asia/Dhaka"))
#     first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     last_day = now

#     doctors = db.query(UserModel).filter(UserModel.user_type == "DOCTOR").all()
#     print("\n--- Monthly Doctor Report ---")

#     for doctor in doctors:
#         appointments = db.query(Appointment).filter(
#             Appointment.doctor_id == doctor.id,
#             Appointment.appointment_date >= first_day,
#             Appointment.appointment_date <= last_day,
#             Appointment.status == "COMPLETED"
#         ).all()

#         total_appointments = len(appointments)
#         earnings = total_appointments * (doctor.consultation_fee or 0)

#         print(f"Doctor: {doctor.full_name}")
#         print(f"  Total Visits: {total_appointments}")
#         print(f"  Total Earnings: {earnings} BDT")
#         print("")

#     db.close()
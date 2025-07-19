from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.models import Appointment
from app.data.schemas.appointment.appointmentschema import AppointmentUpdate, AppointmentStatus


def update_appointment_by_admin(
    db: Session,
    appointment_id: int,
    update_data: AppointmentUpdate
) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    data = update_data.dict(exclude_unset=True)

    if 'appointment_date' in data:
        new_date = data['appointment_date']
    if new_date != appointment.appointment_date:
        # Check for conflicts only if changing date
        conflict = db.query(Appointment).filter(
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == new_date,
            Appointment.id != appointment.id,  # exclude self
            Appointment.status != AppointmentStatus.CANCELLED
        ).first()

        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time slot already booked"
            )

    for field, value in data.items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)
    return appointment

def update_appointment_status_by_doctor(
    db: Session,
    doctor_id: int,
    appointment_id: int,
    new_status: AppointmentStatus
) -> Appointment:
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == doctor_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found or unauthorized")

    appointment.status = new_status
    db.commit()
    db.refresh(appointment)
    return appointment

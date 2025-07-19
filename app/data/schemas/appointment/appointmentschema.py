from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Any, List
import re
import enum
from datetime import datetime, timezone



class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: datetime
    notes: Optional[str] = None

    @field_validator('appointment_date')
    @classmethod
    def validate_future_date(cls, v: datetime):
        now = datetime.now(timezone.utc)

        if v.tzinfo is None:  # Convert naive datetime to aware
            v = v.replace(tzinfo=timezone.utc)

        if v < now:
            raise ValueError("Appointment date must be in the future")
        return v

    
class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None

    @field_validator('appointment_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        return v

    @field_validator('appointment_date')
    @classmethod
    def validate_future_date(cls, v: datetime):
        if v:
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if v < now:
                raise ValueError("Appointment date must be in the future")
        return v

class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    notes: Optional[str] = None
    status: AppointmentStatus
    
    class Config:
        from_attributes = True

class SpecializationOut(BaseModel):
    id: int
    specialized: str
    description: Optional[str]

    class Config:
        orm_mode = True

class DoctorResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]
    license_number: Optional[str]
    experience_years: Optional[int]
    consultation_fee: Optional[int]
    available_timeslots: Optional[str]
    specializations: List[SpecializationOut] = []

    class Config:
        orm_mode = True

class DoctorReportBase(BaseModel):
    doctor_id: int
    month: int
    year: int
    total_patient_visits: int
    total_appointments: int
    total_earnings: float
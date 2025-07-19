from datetime import datetime
from sqlalchemy import Table, Column, Integer, Text, String, Boolean,Enum, DateTime, ForeignKey, JSON, func, TIMESTAMP, DECIMAL,Float,Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from app.config import config
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
import enum
SQLALCHEMY_DATABASE_SCHEMA = config.POSTGRES_SCHEMA

metadata = MetaData(schema=SQLALCHEMY_DATABASE_SCHEMA)  # Define the schema

Base = declarative_base(metadata=metadata)

class UserType(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    
class StatusType(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String(14), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    division = Column(String)
    district = Column(String)
    thana = Column(String)
    profile_image = Column(String)
    license_number = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Integer, nullable=True)
    available_timeslots = Column(String, nullable=True)

    specializations = relationship("DoctorSpecialization", back_populates="doctor", cascade="all, delete")
    status = Column(Enum(StatusType), default=StatusType.ACTIVE)

class DoctorSpecialization(Base):
    __tablename__ = "doctor_specializations"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)
    specialized = Column(String(200))
    description = Column(String(500))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    doctor = relationship("UserModel", back_populates="specializations")

class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)
    status = Column(SQLEnum(AppointmentStatus, name="appointment_status_enum"), default=AppointmentStatus.PENDING)
    created_at = Column(DateTime, server_default="now()")



class PeriodicTaskModel(Base):
    __tablename__ = 'periodic_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(200), unique=True)
    task_path = Column(String(200))
    cron_syntax = Column(String(100))  # Interval in seconds
    args = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DoctorReport(Base):
    __tablename__ = "doctor_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    total_patient_visits = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    generated_at = Column(Date, server_default=func.now())
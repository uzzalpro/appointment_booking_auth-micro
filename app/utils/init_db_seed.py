import os
from datetime import datetime, timedelta
from enum import Enum
from typing import List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Float, Date, Time, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
import bcrypt

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:BA123456@localhost:3432/business_automation")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# Enums
class UserType(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    
class StatusType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

# Models (same as you provided)
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile = Column(String(14), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False)
    division = Column(String)
    district = Column(String)
    thana = Column(String)
    profile_image = Column(String)
    license_number = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Integer, nullable=True)
    available_timeslots = Column(String, nullable=True)
    status = Column(SQLEnum(StatusType), default=StatusType.ACTIVE)

    specializations = relationship("DoctorSpecialization", back_populates="doctor", cascade="all, delete")
    appointments_as_doctor = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    appointments_as_patient = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")

class DoctorSpecialization(Base):
    __tablename__ = "doctor_specializations"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)
    specialized = Column(String(200))
    description = Column(String(500))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    doctor = relationship("UserModel", back_populates="specializations")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)
    status = Column(SQLEnum(AppointmentStatus, name="appointment_status_enum"), default=AppointmentStatus.PENDING)
    created_at = Column(DateTime, server_default="now()")

    patient = relationship("UserModel", foreign_keys=[patient_id], back_populates="appointments_as_patient")
    doctor = relationship("UserModel", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")


def init_db():
    Base.metadata.create_all(bind=engine)
    
# Password hashing
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_data():
    db = SessionLocal()
    
    try:
        # Create admin user
        admin = UserModel(
            full_name="Admin User",
            email="admin@example.com",
            mobile="+8801711111111",
            hashed_password=get_password_hash("Admin@123"),
            user_type=UserType.ADMIN,
            division="Dhaka",
            district="Dhaka",
            thana="Mirpur",
            status=StatusType.ACTIVE
        )
        db.add(admin)

        # Create doctors
        doctors = [
            UserModel(
                full_name=f"Dr. {name}",
                email=f"dr.{name.lower()}@example.com",
                mobile=f"+8801712{1000 + i}",
                hashed_password=get_password_hash(f"Doctor@{i+1}"),
                user_type=UserType.DOCTOR,
                division="Dhaka",
                district="Dhaka",
                thana=thana,
                license_number=f"MED-2023-{1000 + i}",
                experience_years=5 + i,
                consultation_fee=500 + (i * 100),
                available_timeslots="09:00-17:00",
                status=StatusType.ACTIVE
            ) for i, (name, thana) in enumerate([
                ("Smith", "Nawabganj"),
                ("Johnson", "Keraniganj"),
                ("Williams", "Savar"),
                ("Brown", "Dohar")
            ])
        ]
        db.add_all(doctors)

        # Create patients
        patients = [
            UserModel(
                full_name=f"Patient {i+1}",
                email=f"patient{i+1}@example.com",
                mobile=f"+8801713{1000 + i}",
                hashed_password=get_password_hash(f"Patient@{i+1}"),
                user_type=UserType.PATIENT,
                division="Dhaka",
                district="Dhaka",
                thana=thana,
                status=StatusType.ACTIVE
            ) for i, thana in enumerate(["Dohar", "Savar", "Keraniganj", "Nawabganj", "Dhamrai"])
        ]
        db.add_all(patients)

        db.commit()

        # Add specializations for doctors
        specializations = [
            DoctorSpecialization(
                doctor_id=doctors[0].id,
                specialized="Cardiology",
                description="Heart specialist"
            ),
            DoctorSpecialization(
                doctor_id=doctors[0].id,
                specialized="Internal Medicine",
                description="General physician"
            ),
            DoctorSpecialization(
                doctor_id=doctors[1].id,
                specialized="Neurology",
                description="Brain and nervous system specialist"
            ),
            DoctorSpecialization(
                doctor_id=doctors[2].id,
                specialized="Pediatrics",
                description="Child specialist"
            ),
            DoctorSpecialization(
                doctor_id=doctors[3].id,
                specialized="Dermatology",
                description="Skin specialist"
            )
        ]
        db.add_all(specializations)

        # Create appointments
        appointments = []
        for i in range(10):
            patient_id = patients[i % len(patients)].id
            doctor_id = doctors[i % len(doctors)].id
            appointment_date = datetime.now() + timedelta(days=i+1)
            
            appointments.append(Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                notes=f"Patient complaint {i+1}",
                status=AppointmentStatus.PENDING if i % 3 == 0 else 
                      AppointmentStatus.CONFIRMED if i % 3 == 1 else 
                      AppointmentStatus.COMPLETED
            ))

        db.add_all(appointments)
        # Create appointments with properly formatted datetime
        appointments = []
        for i in range(10):
            patient_id = patients[i % len(patients)].id
            doctor_id = doctors[i % len(doctors)].id
            # Create datetime objects for appointments at specific times
            appointment_date = (datetime.now() + timedelta(days=i+1)).replace(
                hour=9 + (i % 8),  # Appointments between 9 AM and 5 PM
                minute=0 if i % 2 == 0 else 30,
                second=0,
                microsecond=0
            )
            
            appointments.append(Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                notes=f"Patient complaint {i+1}",
                status=AppointmentStatus.PENDING if i % 3 == 0 else 
                    AppointmentStatus.CONFIRMED if i % 3 == 1 else 
                    AppointmentStatus.COMPLETED
            ))

        db.add_all(appointments)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Seeding data...")
    seed_data()
    print("Database setup and seeding completed successfully!")
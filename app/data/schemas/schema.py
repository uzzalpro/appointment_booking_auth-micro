from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, Any, List
import re
import enum
from datetime import datetime, date



class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)
    
class UserType(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

class StatusType(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class DoctorSpecializationOut(BaseModel):
    id: int
    specialized: str
    description: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True





# class UserCreateSchema(BaseModel):
#     full_name: str = Field(..., min_length=1)
#     email: EmailStr
#     mobile: str
#     password: str
#     user_type: UserType
#     division: Optional[str] = None
#     district: Optional[str] = None
#     thana: Optional[str] = None
#     license_number: Optional[str] = None
#     experience_years: Optional[int] = Field(None, ge=0)
#     consultation_fee: Optional[int] = Field(None, ge=0)
#     available_timeslots: Optional[str] = None
#     status: Optional[StatusType] = None

#     class Config:
#         from_attributes = True

class UserCreateSchema(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    mobile: str
    password: str
    user_type: UserType
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]
    license_number: Optional[str]
    experience_years: Optional[int] = Field(None, ge=0)
    consultation_fee: Optional[int] = Field(None, ge=0)
    available_timeslots: Optional[str]
    status: Optional[StatusType] = StatusType.ACTIVE

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not v.startswith('+') or not v[1:].isdigit():
            raise ValueError('Mobile must start with + and contain only digits after')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least 1 digit')
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError('Password must contain at least 1 special character')
        return v

    @field_validator('user_type', mode='before')
    @classmethod
    def validate_user_type(cls, v: str) -> UserType:
        if isinstance(v, UserType):
            return v
        try:
            return UserType(v.lower())
        except ValueError:
            raise ValueError(f"Invalid user type. Must be one of: {[e.value for e in UserType]}")
        


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    password: Optional[str] = None
    user_type: Optional[UserType] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    consultation_fee: Optional[int] = Field(None, ge=0)
    available_timeslots: Optional[str] = None
    status: Optional[StatusType] = None

    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        if not v.startswith('+') or not v[1:].isdigit():
            raise ValueError('Mobile must start with + and contain only digits after')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least 1 digit')
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError('Password must contain at least 1 special character')
        return v

    @field_validator('user_type', mode='before')
    @classmethod
    def validate_user_type(cls, v: str) -> UserType:
        if isinstance(v, UserType):
            return v
        try:
            return UserType(v.lower())
        except ValueError:
            raise ValueError(f"Invalid user type. Must be one of: {[e.value for e in UserType]}")


class UserOutSchema(BaseModel):
    id: int
    profile_image: Optional[str]
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    user_type: Optional[UserType] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    consultation_fee: Optional[int] = Field(None, ge=0)
    available_timeslots: Optional[str] = None
    status: Optional[StatusType] = None

    specializations: List[DoctorSpecializationOut] = []

    class Config:
        orm_mode = True
        fields = {'password': {'exclude': True}}

class DoctorSpecializationIn(BaseModel):
    specialized: str
    description: Optional[str] = None
class DoctorUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    # password: Optional[str] = None
    user_type: Optional[UserType] = None
    division: Optional[str] = None
    district: Optional[str] = None
    thana: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    consultation_fee: Optional[int] = Field(None, ge=0)
    available_timeslots: Optional[str] = None
    status: Optional[StatusType] = None
    # ... other fields ...
    specializations: Optional[List[DoctorSpecializationIn]]
    class Config:
        orm_mode = True
        fields = {'password': {'exclude': True}}


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    id:int
    user_type: str  # New field added
    full_name: Optional[str] = None
    available_timeslots: Optional[str] = None
    access_token: str
    token_type: str = "bearer"



class PatientResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    division: Optional[str]
    district: Optional[str]
    thana: Optional[str]

    class Config:
        from_attributes = True


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
    user_type: Optional[UserType] = None
    specializations: Optional[List[DoctorSpecializationIn]]

    class Config:
        from_attributes = True  # Enables ORM mode (same as orm_mode = True)


class DoctorReportBase(BaseModel):
    doctor_id: int
    month: int
    year: int
    total_patient_visits: int
    total_appointments: int
    total_earnings: float

class DoctorReportSchema(DoctorReportBase):
    id: int
    generated_at: date

    class Config:
        from_attributes = True

class MonthlySummarySchema(BaseModel):
    total_patients: int
    total_appointments: int
    total_earnings: float
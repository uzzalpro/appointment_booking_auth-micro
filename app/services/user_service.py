
from sqlalchemy.orm import Session
from typing import Optional, Any, List
from app.db.models.models import UserModel, DoctorSpecialization
from app.data.schemas.schema import UserCreateSchema, UserUpdateSchema, UserType
from app.utils.authpasshash import get_password_hash, verify_password, create_jwt_token, create_access_token
from app.utils.file_upload import save_uploaded_file
from app.utils.location_data import get_upazilas
from app.utils.validators import validate_image_file
from fastapi import Depends, HTTPException, status, BackgroundTasks, FastAPI, Query
from sqlalchemy.exc import IntegrityError
from fastapi.datastructures import UploadFile
from sqlalchemy.orm import joinedload

def is_unique_email(db: Session, email: str) -> bool:
    return not db.query(UserModel).filter_by(email=email).first()


def is_unique_mobile(db: Session, mobile: str) -> bool:
    return not db.query(UserModel).filter_by(mobile=mobile).first()


def create_user(db: Session, user_data: UserCreateSchema) -> UserModel:
    if not is_unique_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if not is_unique_mobile(db, user_data.mobile):
        raise HTTPException(status_code=400, detail="Mobile number already in use")

    hashed_pw = get_password_hash(user_data.password)
    user = UserModel(
        full_name=user_data.full_name,
        email=user_data.email,
        mobile=user_data.mobile,
        hashed_password=hashed_pw,
        user_type=user_data.user_type,
        division=user_data.division,
        district=user_data.district,
        thana=user_data.thana,
        license_number=user_data.license_number,
        experience_years=user_data.experience_years,
        consultation_fee=user_data.consultation_fee,
        available_timeslots=user_data.available_timeslots,
        status=user_data.status
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def update_user(db: Session, user_id: int, update_data: UserUpdateSchema) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = update_data.dict(exclude_unset=True)

    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))

    for key, value in data.items():
        setattr(user, key, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or mobile already in use")

    return user


# def get_all_doctors(db: Session) -> List[UserModel]:
#     return db.query(UserModel).filter(UserModel.user_type == UserType.DOCTOR).all()



def get_all_doctors(db: Session) -> List[UserModel]:
    return (
        db.query(UserModel)
        .filter(UserModel.user_type == UserType.DOCTOR)
        .options(joinedload(UserModel.specializations))  # 👈 eager load
        .all()
    )


from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime

def update_doctor_by_admin(
    db: Session, doctor_id: int, update_data: UserUpdateSchema
) -> UserModel:
    doctor = db.query(UserModel).filter(
        UserModel.id == doctor_id,
        UserModel.user_type == UserType.DOCTOR
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    data = update_data.dict(exclude_unset=True)

    # Handle password
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))

    # Handle specializations separately
    specializations_data = data.pop("specializations", None)

    # Update regular fields
    for key, value in data.items():
        setattr(doctor, key, value)

    # Update specializations
    if specializations_data is not None:
        # Clear old ones
        doctor.specializations.clear()
        # Add new ones
        for spec in specializations_data:
            doctor.specializations.append(
                DoctorSpecialization(
                    specialized=spec["specialized"],
                    description=spec.get("description"),
                    created_at=datetime.utcnow()
                )
            )

    try:
        db.commit()
        db.refresh(doctor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or mobile already in use")

    return doctor

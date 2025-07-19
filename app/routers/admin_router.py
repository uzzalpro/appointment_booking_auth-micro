
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import traceback
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, FastAPI, Query
from sqlalchemy.orm import Session
from app.config import config

from app.data.schemas.commonschema import (ResponseSchema)
from app.data.schemas.schema import UserCreateSchema, UserType, UserLoginSchema, TokenSchema, StatusType, PatientResponse, DoctorResponse, UserOutSchema, UserUpdateSchema
from app.db.models.models import UserModel, DoctorSpecialization

from app.db.session import get_db
from app.dependencies.auth import get_current_user_id, get_current_user

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from app.utils.validators import validate_image_file

from dotenv import load_dotenv
from app.utils.file_upload import save_uploaded_file
from app.utils.location_data import get_upazilas

from app.services.user_service import (get_all_doctors, update_doctor_by_admin)

admin_router = APIRouter(
    prefix=f"{config.API_PREFIX}",
    tags=['Admin']
)


@admin_router.get("/get-doctor-list", response_model=List[UserOutSchema], status_code=status.HTTP_201_CREATED)
async def get_all_doctor_users(db: Session = Depends(get_db)):
    """
    Admin-only endpoint: List all doctors in the system.
    """
    return get_all_doctors(db)


from fastapi import Form, File, UploadFile

@admin_router.put("/doctors/{user_id}")
async def update_doctor(
    user_id: int,
    full_name: Optional[str] = Form(None),
    specialization: Optional[str] = Form(None),
    experience_years: Optional[int] = Form(None),
    consultation_fee: Optional[int] = Form(None),
    division: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    thana: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),  # if image later
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    user_data = {
        "full_name": full_name,
        "experience_years": experience_years,
        "consultation_fee": consultation_fee,
        "division": division,
        "district": district,
        "thana": thana,
    }

    # Parse specialization JSON string into list of dicts
    if specialization:
        import json
        try:
            user_data["specializations"] = json.loads(specialization)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid specializations JSON")

    # Call your update function
    return update_doctor_by_admin(db, user_id, UserUpdateSchema(**user_data))


# @admin_router.put("/doctors/{doctor_id}", response_model=UserOutSchema)
# async def update_doctor_profile(doctor_id: int, payload: UserUpdateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
#     """
#     Admin-only endpoint: Update any doctor's profile.
#     """
#     if current_user.user_type != UserType.ADMIN.value:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only admin users can access this resource"
#         )
#     return update_doctor_by_admin(db, doctor_id, payload)


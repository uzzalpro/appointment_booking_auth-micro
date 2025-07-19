import logging
from typing import List, Optional, Union
from datetime import datetime, timedelta
import traceback
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, FastAPI, Query
from sqlalchemy.orm import Session
from app.config import config

from app.data.schemas.commonschema import (ResponseSchema)
from app.data.schemas.schema import UserCreateSchema, UserType, UserLoginSchema, TokenSchema, StatusType, PatientResponse, DoctorResponse, UserOutSchema, UserUpdateSchema
from app.db.models.models import UserModel, DoctorSpecialization
import os
from app.db.session import get_db
from app.dependencies.auth import get_current_user_id
from app.utils.authpasshash import get_password_hash, verify_password, create_jwt_token, create_access_token
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form,File
from app.utils.validators import validate_image_file, validate_image

from dotenv import load_dotenv
from app.utils.file_upload import save_uploaded_file
from app.utils.location_data import get_upazilas
from app.services.user_service import (create_user, get_user, update_user)
import time

UPLOAD_DIR = "static/uploads"

user_auth_router = APIRouter(
    prefix=f"{config.API_PREFIX}",
    tags=['Authuser']
)


@user_auth_router.post("/user-register", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        return create_user(db, payload)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@user_auth_router.get("/get-user/{user_id}", response_model=UserOutSchema, status_code=status.HTTP_200_OK)
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_auth_router.put("/update-user/{user_id}", response_model=UserOutSchema, status_code=status.HTTP_200_OK)

async def update_user_info(
    user_id: int,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    mobile: Optional[str] = Form(None),
    division: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    thana: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    license_number: Optional[str] = Form(None),
    experience_years: Optional[int] = Form(None),
    consultation_fee: Optional[int] = Form(None),
    available_timeslots: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Create payload from form data
    payload_data = {
        "full_name": full_name,
        "email": email,
        "mobile": mobile,
        "division": division,
        "district": district,
        "thana": thana,
        "license_number":license_number,
        "experience_years":experience_years,
        "consultation_fee":consultation_fee,
        "available_timeslots":available_timeslots


    }
    
    # Validate with your schema
    payload = UserUpdateSchema(**{k: v for k, v in payload_data.items() if v is not None})
    
    # Update user info
    updated_user = update_user(db, user_id, payload)
    
    # Handle image upload if present
    if image:
        try:
            # Validate image
            await validate_image(image)
            
            # Prepare upload directory
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            
            # Generate unique filename
            file_ext = os.path.splitext(image.filename)[1].lower()
            filename = f"user_{user_id}_{int(time.time())}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save the file
            contents = await image.read()
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            # Update the user's profile image path in database
            # First remove old image if exists
            if updated_user.profile_image:
                old_image_path = os.path.join(UPLOAD_DIR, updated_user.profile_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save relative path in database
            updated_user.profile_image = filename
            db.commit()
            db.refresh(updated_user)
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    return updated_user



@user_auth_router.post("/login", response_model=ResponseSchema)
def login(user_credentials: UserLoginSchema, db: Session = Depends(get_db)):
    # Fetch user by email
    user = db.query(UserModel).filter(UserModel.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Generate token
    token_data = {"sub": str(user.id), "user_type": user.user_type.value}
    access_token = create_access_token(data=token_data)

    return ResponseSchema(
        success=True,
        message="Login successful",
        data=TokenSchema(
            id=user.id,
            user_type=user.user_type.value,
            full_name=user.full_name,
            available_timeslots=user.available_timeslots,
            access_token=access_token,
            token_type="bearer"
            
        )
    )

@user_auth_router.get("/doctors/search", response_model=List[DoctorResponse])
def search_doctors(
    keyword: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
    division: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    thana: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(UserModel).filter(
    UserModel.user_type.in_([UserType.DOCTOR, UserType.PATIENT])
)
    
    if specialization:
        query = query.join(UserModel.specializations).filter(
            DoctorSpecialization.specialized.ilike(f"%{specialization}%")
        )
    
    if keyword:
        keyword = f"%{keyword.lower()}%"
        query = query.filter(
            (UserModel.full_name.ilike(keyword)) |
            (UserModel.email.ilike(keyword)) |
            (UserModel.mobile.ilike(keyword))
        )
    
    if division:
        query = query.filter(UserModel.division.ilike(f"%{division}%"))
    
    if district:
        query = query.filter(UserModel.district.ilike(f"%{district}%"))
    
    if thana:
        query = query.filter(UserModel.thana.ilike(f"%{thana}%"))
    
    if is_available is not None:
        query = query.filter(UserModel.is_available == is_available)
    
    return query.all()
# def search_doctors(
#     keyword: Optional[str] = Query(None, description="Search by name, email, specialization, division, district, thana or mobile"),
#     skip: int = 0,
#     limit: int = 10,
#     db: Session = Depends(get_db)
# ):
#     query = db.query(UserModel).filter(
#     UserModel.user_type.in_([UserType.DOCTOR, UserType.PATIENT])
# )

#     if keyword:
#         keyword = f"%{keyword.lower()}%"
#         query = query.filter(
#             (UserModel.full_name.ilike(keyword)) |
#             (UserModel.email.ilike(keyword)) |
#             (UserModel.mobile.ilike(keyword))
#         )

#     results = query.offset(skip).limit(limit).all()
#     return results


"""
update profile (endpoint -1)
book appointments, (endpoint -1) --> update (for admin, and doctor)
view their booking history (endpoint -1) --> get (for indivisual user)
Doctor manage their schedule(profile), view their appointments, and update appointment status
admin manage all appointments, doctors, and generate reports
"""



# @user_auth_router.post("/user-register", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
# async def register(
#     full_name: str = Form(...),
#     email: str = Form(...),
#     mobile: str = Form(...),
#     password: str = Form(...),
#     user_type: str = Form(...),
#     division: str = Form(None),
#     district: str = Form(None),
#     thana: str = Form(None),
#     license_number: str = Form(None),
#     experience_years: str = Form(None),
#     consultation_fee: str = Form(None),
#     profile_image: UploadFile = File(None),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Convert types
#         try:
#             user_type_enum = UserType(user_type.lower())
#         except ValueError:
#             raise HTTPException(status_code=422, detail=f"Invalid user_type: {user_type}")
        
#         experience_years_int = int(experience_years) if experience_years and experience_years.strip() else None
#         consultation_fee_int = int(consultation_fee) if consultation_fee and consultation_fee.strip() else None

#         # Validate phone
#         if not mobile.startswith("+") or not mobile[1:].isdigit():
#             raise HTTPException(status_code=422, detail="Mobile must start with '+' and digits only")

#         # Check user exists
#         existing = db.query(UserModel).filter(
#             (UserModel.email == email) | (UserModel.mobile == mobile)
#         ).first()
#         if existing:
#             raise HTTPException(status_code=400, detail="User already exists")

#         # Validate location
#         if thana and (not division or not district):
#             raise HTTPException(status_code=422, detail="Thana needs both division and district")
#         if thana:
#             valid_upazilas = get_upazilas(division, district)
#             if thana not in valid_upazilas:
#                 raise HTTPException(status_code=422, detail=f"Invalid thana for {district}, {division}")

#         # Validate doctor fields
#         if user_type_enum == UserType.DOCTOR:
#             if not all([license_number, experience_years_int is not None, consultation_fee_int is not None]):
#                 raise HTTPException(status_code=422, detail="Doctor fields are required")

#         # Save image or default
#         if profile_image:
#             profile_image_path = await save_uploaded_file(profile_image)
#         else:
#             profile_image_path = "default.jpg"

#         # Create user
#         user = UserModel(
#             full_name=full_name,
#             email=email,
#             mobile=mobile,
#             hashed_password=get_password_hash(password),
#             user_type=user_type_enum,
#             division=division,
#             district=district,
#             thana=thana,
#             profile_image=profile_image_path,
#             license_number=license_number,
#             experience_years=experience_years_int,
#             consultation_fee=consultation_fee_int,
#             status=StatusType.ACTIVE
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         return ResponseSchema(
#             success=True,
#             message="User registered successfully",
#             data={"id": user.id, "email": user.email, "user_type": user.user_type.value}
#         )

#     except HTTPException:
#         db.rollback()
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
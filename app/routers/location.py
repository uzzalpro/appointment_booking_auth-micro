# app/routers/location.py
from fastapi import APIRouter, HTTPException
from app.data.schemas.commonschema import DivisionResponse, DistrictResponse, UpazilaResponse
from app.utils.location_data import (
    get_divisions,
    get_districts,
    get_upazilas
)
import enum
from app.config import config

location_router = APIRouter(
    prefix=f"{config.API_PREFIX}",
    tags=['Location']
)

@location_router.get("/divisions", response_model=DivisionResponse)
async def get_all_divisions():
    return {"divisions": get_divisions()}

@location_router.get("/districts/{division}", response_model=DistrictResponse)
async def get_districts_by_division(division: str):
    try:
        districts = get_districts(division)
        if not districts:
            raise HTTPException(
                status_code=404,
                detail=f"No districts found for division: {division}"
            )
        return {"districts": districts}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@location_router.get("/upazilas/{division}/{district}", response_model=UpazilaResponse)
async def get_upazilas_by_district(division: str, district: str):
    try:
        upazilas = get_upazilas(division, district)
        if not upazilas:
            raise HTTPException(
                status_code=404,
                detail=f"No upazilas found for {district}, {division}"
            )
        return {"upazilas": upazilas}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

class UserType(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

@location_router.get("/user-types", response_model=list[str])
async def get_user_types():
    """Get all available user types"""
    return [member.value for member in UserType]
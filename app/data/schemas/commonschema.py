from pydantic import BaseModel, field_validator, ValidationError, ValidationInfo, EmailStr
from typing import Generic, TypeVar, Optional
from decimal import Decimal
from enum import Enum as PyEnum
import json
from xml.etree import ElementTree
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import List
from app.utils.location_data import get_divisions, get_districts, get_upazilas


T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None





class DivisionResponse(BaseModel):
    divisions: List[str]

class DistrictResponse(BaseModel):
    districts: List[str]

class UpazilaResponse(BaseModel):
    upazilas: List[str]

class LocationCreate(BaseModel):
    division: str
    district: str
    thana: str

    @field_validator('division')
    @classmethod
    def validate_division(cls, v: str) -> str:
        divisions = get_divisions()
        if v not in divisions:
            raise ValueError(f"Invalid division. Must be one of: {', '.join(divisions)}")
        return v

    @field_validator('district')
    @classmethod
    def validate_district(cls, v: str, values: dict) -> str:
        if 'division' not in values:
            raise ValueError("Division must be provided first")
        
        districts = get_districts(values['division'])
        if v not in districts:
            raise ValueError(f"Invalid district for {values['division']}. Must be one of: {', '.join(districts)}")
        return v

    @field_validator('thana')
    @classmethod
    def validate_thana(cls, v: str, values: dict) -> str:
        if 'division' not in values or 'district' not in values:
            raise ValueError("Division and district must be provided first")
        
        upazilas = get_upazilas(values['division'], values['district'])
        if v not in upazilas:
            raise ValueError(f"Invalid thana for {values['district']}. Must be one of: {', '.join(upazilas)}")
        return v
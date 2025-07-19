from pydantic import field_validator, Field, BaseModel
from datetime import datetime
import re
from fastapi import UploadFile

from fastapi import UploadFile, File, Form, HTTPException
import os
from pathlib import Path
from typing import Optional
from PIL import Image  # or whatever PIL functionality you need
import io

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]


def validate_image_file(file: UploadFile):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise ValueError("Only JPEG/PNG images allowed")
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValueError("File size exceeds 5MB")
    return file

async def validate_image(image: UploadFile):
    # Check file size
    if image.size > MAX_FILE_SIZE:
        raise ValueError(f"Image too large. Max size is {MAX_FILE_SIZE/1024/1024}MB")
    
    # Check content type
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Only JPEG or PNG images are allowed")
    
    # Verify the file is actually an image by trying to open it
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        img.verify()  # Verify that it is, in fact, an image
        await image.seek(0)  # Reset file pointer after reading
    except Exception:
        raise ValueError("Invalid image file")
    
def validate_timeslot(start: datetime, end: datetime):
    if start >= end:
        raise ValueError("End time must be after start time")
    if start.hour < 9 or end.hour > 17:
        raise ValueError("Appointments only available between 9AM-5PM")
    return start, end

class AppointmentCreate(BaseModel):
    doctor_id: int
    date_time: datetime
    notes: str = Field(None, max_length=500)
    
    @field_validator('date_time')
    @classmethod
    def validate_future_datetime(cls, v: datetime) -> datetime:
        if v < datetime.now():
            raise ValueError("Appointment date cannot be in the past")
        return v
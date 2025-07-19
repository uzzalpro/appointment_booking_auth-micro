import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Optional
from uuid import uuid4

# Define the base directory for your project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_uploaded_file(
    file: UploadFile, 
    allowed_types: list = ["image/jpeg", "image/png"],
    max_size: int = 5 * 1024 * 1024  # 5MB
) -> Optional[str]:
    """
    Save uploaded file to static/uploads directory
    Returns relative file path if successful, None otherwise
    """
    try:
        # Validate file type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Only {', '.join(allowed_types)} files are allowed"
            )

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset pointer
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size is {max_size//(1024*1024)}MB"
            )

        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid4().hex}{file_ext}"
        file_path = UPLOAD_DIR / filename

        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return f"uploads/{filename}"

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.db.session import get_db
from app.db.models.models import DoctorReport
from app.data.schemas.schema import DoctorReportSchema, MonthlySummarySchema
from app.config import config
from app.services.reports_service import (generate_monthly_reports)
from typing import List
from sqlalchemy import func, extract,distinct

report_router = APIRouter(
    prefix=f"{config.API_PREFIX}",
    tags=['Report']
)

@report_router.post("/generate-monthly", response_model=List[DoctorReportSchema])
async def generate_monthly_report_endpoint(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    """
    Generate monthly reports for all doctors
    - Requires month (1-12) and year (>=2000) parameters
    - Returns list of generated reports
    """
    try:
        return generate_monthly_reports(db, month, year)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@report_router.get("/monthly", response_model=List[DoctorReportSchema])
async def get_monthly_reports(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    doctor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get monthly reports with optional filters"""
    query = db.query(DoctorReport)
    
    if month is not None:
        query = query.filter(DoctorReport.month == month)
    if year is not None:
        query = query.filter(DoctorReport.year == year)
    if doctor_id is not None:
        query = query.filter(DoctorReport.doctor_id == doctor_id)
    
    return query.order_by(
        DoctorReport.year.desc(),
        DoctorReport.month.desc()
    ).all()

@report_router.get("/monthly-summary", response_model=MonthlySummarySchema)
async def get_monthly_summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db)
):
    """Get summary of all monthly reports"""
    query = db.query(
        func.sum(DoctorReport.total_patient_visits).label("total_patients"),
        func.sum(DoctorReport.total_appointments).label("total_appointments"),
        func.sum(DoctorReport.total_earnings).label("total_earnings")
    )
    
    if month is not None:
        query = query.filter(DoctorReport.month == month)
    if year is not None:
        query = query.filter(DoctorReport.year == year)
    
    result = query.first()
    
    return {
        "total_patients": result[0] or 0,
        "total_appointments": result[1] or 0,
        "total_earnings": result[2] or 0
    }

# async def get_monthly_summary(
#     month: Optional[int] = Query(None, ge=1, le=12),
#     year: Optional[int] = Query(None, ge=2000),
#     db: Session = Depends(get_db)
# ):
#     """Get summary of all monthly reports"""
#     try:
#         query = db.query(
#             func.sum(DoctorReport.total_patient_visits).label("total_patients"),
#             func.sum(DoctorReport.total_appointments).label("total_appointments"),
#             func.sum(DoctorReport.total_earnings).label("total_earnings")
#         )
        
#         if month is not None:
#             query = query.filter(DoctorReport.month == month)
#         if year is not None:
#             query = query.filter(DoctorReport.year == year)
        
#         result = query.first()
        
#         if not result or result[0] is None:  # No records found
#             return {
#                 "total_patients": 0,
#                 "total_appointments": 0,
#                 "total_earnings": 0.0
#             }
        
#         return {
#             "total_patients": result[0] or 0,
#             "total_appointments": result[1] or 0,
#             "total_earnings": result[2] or 0.0
#         }
    
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to generate summary: {str(e)}"
#         )
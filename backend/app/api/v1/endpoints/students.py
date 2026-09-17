from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.schemas.student import StudentResponse, TranscriptResponse, ProgressResponse, TokenResponse
from app.services.student_service import StudentService
from app.dependencies import get_student_service
from app.core.auth import create_access_token, verify_password, authorize_student
from app.database.db import db_manager

router = APIRouter()

class LoginRequest(BaseModel):
    student_id: str
    password: str | None = None

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, student_service: StudentService = Depends(get_student_service)):
    student = await student_service.get_student(request.student_id)
    if not student:
        raise HTTPException(status_code=401, detail="Invalid student ID")
    record = await db_manager.get_student_record(request.student_id)
    if record and record.password_hash and (not request.password or not verify_password(request.password, record.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(student.student_id, getattr(record, "role", "student")),
                         student=student)

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str, student_service: StudentService = Depends(get_student_service), _user=Depends(authorize_student)):
    student = await student_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse(student=student)

@router.get("/{student_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(student_id: str, student_service: StudentService = Depends(get_student_service), _user=Depends(authorize_student)):
    student = await student_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    completed_courses = await student_service.get_transcript(student_id)
    return TranscriptResponse(student=student, completed_courses=completed_courses)

@router.get("/{student_id}/progress", response_model=ProgressResponse)
async def get_progress(student_id: str, student_service: StudentService = Depends(get_student_service), _user=Depends(authorize_student)):
    progress_data = await student_service.get_progress(student_id)
    if not progress_data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = await student_service.get_student(student_id)
    return ProgressResponse(
        student=student,
        completed_credits=student.total_credits_completed,
        required_credits=student.total_credits_required,
        completion_percentage=progress_data["completion_percentage"],
        completed_courses=progress_data["completed_courses"],
        remaining_courses=progress_data["remaining_courses"],
        eligible_courses=progress_data["eligible_courses"]
    )

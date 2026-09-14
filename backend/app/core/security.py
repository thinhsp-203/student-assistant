from fastapi import Depends, HTTPException, status
from app.services.student_service import StudentService
from app.dependencies import get_student_service

async def get_current_student(student_id: str, student_service: StudentService = Depends(get_student_service)):
    student = await student_service.get_student(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    return student

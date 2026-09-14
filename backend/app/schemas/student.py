from pydantic import BaseModel
from typing import List, Optional
from app.models.student import Student, CompletedCourse
from app.models.curriculum import Course

class StudentResponse(BaseModel):
    student: Student

class TranscriptResponse(BaseModel):
    student: Student
    completed_courses: List[CompletedCourse]

class ProgressResponse(BaseModel):
    student: Student
    completed_credits: int
    required_credits: int
    completion_percentage: float
    completed_courses: List[CompletedCourse]
    remaining_courses: List[Course]
    eligible_courses: List[Course]

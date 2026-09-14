from pydantic import BaseModel
from typing import List, Optional, Any

class Student(BaseModel):
    student_id: str
    name: str
    email: str
    major: str
    intake_year: int
    current_semester: int
    gpa: float
    total_credits_completed: int
    total_credits_required: int
    status: str
    warnings: Optional[str] = None

class CompletedCourse(BaseModel):
    course_id: str
    course_name: str
    credits: int
    grade: str
    grade_point: float
    semester: int

class StudentTranscript(BaseModel):
    student: Student
    completed_courses: List[CompletedCourse]

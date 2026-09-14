from typing import List
from pydantic import BaseModel, Field

from app.models.curriculum import Course


class BlockedCourse(BaseModel):
    course: Course
    missing_prerequisites: List[str]
    reason: str


class AdvisingResponse(BaseModel):
    student_id: str
    current_semester: int
    target_semester: int
    eligible_courses: List[Course]
    blocked_courses: List[BlockedCourse]
    completed_course_ids: List[str]
    recommendation_reasons: dict[str, str] = Field(default_factory=dict)
    rules: List[str] = Field(default_factory=list)

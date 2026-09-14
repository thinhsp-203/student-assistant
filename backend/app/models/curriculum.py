from pydantic import BaseModel, Field
from typing import List, Optional

class Course(BaseModel):
    course_id: str
    name: str
    credits: int
    prerequisites: List[str] = Field(default_factory=list)
    category: str
    suggested_semester: int
    description: Optional[str] = None

class Curriculum(BaseModel):
    name: str
    total_credits: int
    courses: List[Course]

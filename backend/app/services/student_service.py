from typing import Optional, Dict, Any
import json
from app.models.student import Student
from app.models.curriculum import Course
from app.database.db import db_manager
from app.services.prompt_templates import STUDENT_CONTEXT_TEMPLATE

class StudentService:
    async def get_student(self, student_id: str) -> Optional[Student]:
        return await db_manager.get_student(student_id)

    async def get_transcript(self, student_id: str):
        return await db_manager.get_transcript(student_id)

    async def get_student_context(self, student_id: str) -> str:
        student = await self.get_student(student_id)
        if not student:
            return ""
        
        transcript = await self.get_transcript(student_id)
        completed_courses_str = ", ".join([f"{c.course_name} ({c.grade})" for c in transcript])
        
        warnings_str = "Không có"
        if student.warnings:
            try:
                warnings_list = json.loads(student.warnings)
                if warnings_list:
                    warnings_str = ", ".join(warnings_list)
            except json.JSONDecodeError:
                pass

        return STUDENT_CONTEXT_TEMPLATE.format(
            name=student.name,
            student_id=student.student_id,
            major=student.major,
            current_semester=student.current_semester,
            gpa=student.gpa,
            credits_completed=student.total_credits_completed,
            credits_required=student.total_credits_required,
            completed_courses_list=completed_courses_str,
            warnings=warnings_str
        )

    async def get_progress(self, student_id: str) -> Dict[str, Any]:
        student = await self.get_student(student_id)
        if not student:
            return {}
            
        completed_courses = await self.get_transcript(student_id)
        
        # This is a simplified progress calculation.
        # In a real system, you would load the curriculum and compare.
        return {
            "completed_courses": [c.model_dump() for c in completed_courses],
            "remaining_courses": [], # Requires curriculum db to populate
            "completion_percentage": (student.total_credits_completed / student.total_credits_required * 100) if student.total_credits_required > 0 else 0,
            "eligible_courses": [] # Requires prerequisite checking logic
        }

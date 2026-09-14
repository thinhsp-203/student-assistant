from typing import List

from app.database.db import Database, db_manager
from app.schemas.advising import AdvisingResponse, BlockedCourse


class AdvisingService:
    """Deterministic prerequisite and next-semester recommendation rules."""

    def __init__(self, database: Database = db_manager):
        self.database = database

    async def recommend(self, student_id: str, target_semester: int | None = None) -> AdvisingResponse | None:
        student = await self.database.get_student(student_id)
        if not student:
            return None
        target = target_semester or student.current_semester + 1
        if target < 1:
            raise ValueError("target_semester must be positive")

        transcript = await self.database.get_transcript(student_id)
        completed = {course.course_id for course in transcript}
        eligible = []
        recommendation_reasons = {}
        blocked: List[BlockedCourse] = []
        for course in await self.database.get_courses():
            if course.course_id in completed or course.suggested_semester > target:
                continue
            missing = sorted(set(course.prerequisites) - completed)
            if missing:
                blocked.append(BlockedCourse(
                    course=course,
                    missing_prerequisites=missing,
                    reason="Còn thiếu môn tiên quyết: " + ", ".join(missing),
                ))
            else:
                eligible.append(course)
                recommendation_reasons[course.course_id] = (
                    "Đủ môn tiên quyết và phù hợp học kỳ mục tiêu "
                    f"{target}."
                )

        def key(item):
            course = item
            category_priority = 0 if course.category in {"Bắt buộc", "Đại cương", "Cơ sở ngành", "Chuyên ngành"} else 1
            return category_priority, course.suggested_semester, course.course_id

        eligible.sort(key=key)
        blocked.sort(key=lambda item: (item.course.suggested_semester, item.course.course_id))
        return AdvisingResponse(
            student_id=student_id,
            current_semester=student.current_semester,
            target_semester=target,
            eligible_courses=eligible,
            blocked_courses=blocked,
            completed_course_ids=sorted(completed),
            recommendation_reasons=recommendation_reasons,
            rules=[
                "Loại bỏ môn đã hoàn thành.",
                "Chỉ đề xuất môn có học kỳ gợi ý không vượt quá học kỳ mục tiêu.",
                "Mọi môn tiên quyết phải có trong bảng điểm.",
            ],
        )

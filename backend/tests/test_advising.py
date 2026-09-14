import asyncio
import tempfile
from pathlib import Path

from app.database.db import Database
from app.services.advising_service import AdvisingService


def test_recommendations_respect_prerequisites():
    async def scenario():
        with tempfile.TemporaryDirectory() as directory:
            database = Database(str(Path(directory) / "students.db"))
            await database.create_tables()
            await database.seed_curriculum(
                [
                    {"course_id": "CS101", "course_name": "Programming", "credits": 3, "semester": 1, "prerequisites": []},
                    {"course_id": "CS201", "course_name": "Data Structures", "credits": 3, "semester": 2, "prerequisites": ["CS101"]},
                ]
            )
            await database.create_student_fixture("S1", ["CS101"])
            result = await AdvisingService(database).recommend("S1")
            assert [course.course_id for course in result.eligible_courses] == ["CS201"]
            assert result.blocked_courses == []

    asyncio.run(scenario())

"""Runnable smoke validation for the SQLite curriculum and advising rules."""
import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import Database
from app.models.curriculum import Course
from app.models.student import Student
from app.services.advising_service import AdvisingService


async def main():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = handle.name
    try:
        database = Database(db_path)
        await database.create_tables()
        await database.replace_courses([
            Course(course_id="A", name="Foundation", credits=3, category="Cơ sở ngành",
                   suggested_semester=1, prerequisites=[]),
            Course(course_id="B", name="Advanced", credits=3, category="Chuyên ngành",
                   suggested_semester=2, prerequisites=["A"]),
        ])
        async with database.get_connection() as db:
            await db.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("S1", "Test Student", "s@example.test", "CNTT", 2025, 1,
                 3.0, 3, 6, "active", None),
            )
            await db.execute(
                "INSERT INTO completed_courses "
                "(student_id, course_id, course_name, credits, grade, grade_point, semester) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("S1", "A", "Foundation", 3, "A", 4.0, 1),
            )
            await db.commit()
        result = await AdvisingService(database).recommend("S1")
        assert result and [item.course_id for item in result.eligible_courses] == ["B"]
        assert not result.blocked_courses
        print("Advising validation passed.")
    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    asyncio.run(main())

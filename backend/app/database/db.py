import aiosqlite
from contextlib import asynccontextmanager
from typing import List, Optional
import json

from app.core.config import settings
from app.models.student import Student, CompletedCourse
from app.models.curriculum import Course

class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url

    @asynccontextmanager
    async def get_connection(self):
        async with aiosqlite.connect(self.db_url) as db:
            db.row_factory = aiosqlite.Row
            yield db

    async def create_tables(self):
        async with self.get_connection() as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    major TEXT NOT NULL,
                    intake_year INTEGER NOT NULL,
                    current_semester INTEGER NOT NULL,
                    gpa REAL NOT NULL,
                    total_credits_completed INTEGER NOT NULL,
                    total_credits_required INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    warnings TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS completed_courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    grade_point REAL NOT NULL,
                    semester INTEGER NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    course_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    credits INTEGER NOT NULL CHECK (credits > 0),
                    category TEXT NOT NULL,
                    suggested_semester INTEGER NOT NULL CHECK (suggested_semester > 0),
                    description TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS course_prerequisites (
                    course_id TEXT NOT NULL,
                    prerequisite_id TEXT NOT NULL,
                    PRIMARY KEY (course_id, prerequisite_id),
                    FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
                    FOREIGN KEY (prerequisite_id) REFERENCES courses (course_id) ON DELETE RESTRICT,
                    CHECK (course_id <> prerequisite_id)
                )
            ''')
            await db.commit()

    async def get_student(self, student_id: str) -> Optional[Student]:
        async with self.get_connection() as db:
            async with db.execute('SELECT * FROM students WHERE student_id = ?', (student_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    data = dict(row)
                    return Student(**data)
        return None

    async def get_transcript(self, student_id: str) -> List[CompletedCourse]:
        async with self.get_connection() as db:
            async with db.execute('SELECT * FROM completed_courses WHERE student_id = ?', (student_id,)) as cursor:
                rows = await cursor.fetchall()
                return [CompletedCourse(**dict(row)) for row in rows]

    async def get_all_students(self) -> List[Student]:
        async with self.get_connection() as db:
            async with db.execute('SELECT * FROM students') as cursor:
                rows = await cursor.fetchall()
                return [Student(**dict(row)) for row in rows]

    async def replace_courses(self, courses: List[Course]) -> None:
        """Replace the catalog atomically; prerequisites are normalized in a join table."""
        async with self.get_connection() as db:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute("DELETE FROM course_prerequisites")
            await db.execute("DELETE FROM courses")
            for course in courses:
                await db.execute(
                    """INSERT INTO courses
                    (course_id, name, credits, category, suggested_semester, description)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (course.course_id, course.name, course.credits, course.category,
                     course.suggested_semester, course.description),
                )
            for course in courses:
                for prerequisite_id in course.prerequisites:
                    await db.execute(
                        """INSERT INTO course_prerequisites (course_id, prerequisite_id)
                        VALUES (?, ?)""",
                        (course.course_id, prerequisite_id),
                    )
            await db.commit()

    async def seed_curriculum(self, courses: list[dict]) -> None:
        """Compatibility helper for fixtures and small local curriculum imports."""
        normalized = [
            Course(
                course_id=item["course_id"],
                name=item.get("name", item.get("course_name")),
                credits=item["credits"],
                category=item.get("category", "Chuyên ngành"),
                suggested_semester=item.get("suggested_semester", item.get("semester", 1)),
                prerequisites=item.get("prerequisites", []),
                description=item.get("description"),
            )
            for item in courses
        ]
        await self.replace_courses(normalized)

    async def create_student_fixture(self, student_id: str, completed_course_ids: list[str]) -> None:
        async with self.get_connection() as db:
            await db.execute(
                """INSERT INTO students
                (student_id, name, email, major, intake_year, current_semester, gpa,
                 total_credits_completed, total_credits_required, status, warnings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (student_id, "Fixture Student", f"{student_id}@example.test", "CNTT",
                 2025, 1, 3.0, 0, 130, "active", None),
            )
            courses = await self.get_courses()
            by_id = {course.course_id: course for course in courses}
            for course_id in completed_course_ids:
                course = by_id[course_id]
                await db.execute(
                    """INSERT INTO completed_courses
                    (student_id, course_id, course_name, credits, grade, grade_point, semester)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (student_id, course_id, course.name, course.credits, "A", 4.0, 1),
                )
            await db.commit()

    async def get_courses(self) -> List[Course]:
        async with self.get_connection() as db:
            query = """
                SELECT c.*, GROUP_CONCAT(cp.prerequisite_id) AS prerequisite_ids
                FROM courses c
                LEFT JOIN course_prerequisites cp ON cp.course_id = c.course_id
                GROUP BY c.course_id
                ORDER BY c.suggested_semester, c.course_id
            """
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            return [
                Course(
                    course_id=row["course_id"],
                    name=row["name"],
                    credits=row["credits"],
                    category=row["category"],
                    suggested_semester=row["suggested_semester"],
                    description=row["description"],
                    prerequisites=(row["prerequisite_ids"].split(",")
                                   if row["prerequisite_ids"] else []),
                )
                for row in rows
            ]

db_manager = Database(settings.SQLITE_DATABASE_URL)

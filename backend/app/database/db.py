import aiosqlite
from contextlib import asynccontextmanager
from typing import List, Optional
import json

from app.core.config import settings
from app.models.student import Student, CompletedCourse

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

db_manager = Database(settings.SQLITE_DATABASE_URL)

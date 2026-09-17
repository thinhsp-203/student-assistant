from contextlib import contextmanager
from typing import List, Optional
from sqlalchemy import create_engine, select, delete, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, selectinload
from app.core.config import settings
from app.models.orm import Base, StudentRecord, CompletedCourseRecord, CourseRecord
from app.models.student import Student, CompletedCourse
from app.models.curriculum import Course


def _url(url: str) -> str:
    return url if "://" in url else f"sqlite:///{url}"


class Database:
    def __init__(self, db_url: str | None = None):
        self.db_url = _url(db_url or settings.database_url)
        kwargs = {"connect_args": {"check_same_thread": False}, "poolclass": NullPool} if self.db_url.startswith("sqlite") else {}
        self.engine = create_engine(self.db_url, future=True, **kwargs)
        self.Session = sessionmaker(self.engine, expire_on_commit=False)

    def __del__(self):
        try:
            self.engine.dispose()
        except Exception:
            pass

    @contextmanager
    def get_connection(self):
        with self.Session() as session:
            yield session

    async def create_tables(self):
        Base.metadata.create_all(self.engine)
        if self.db_url.startswith("sqlite"):
            with self.engine.begin() as conn:
                for column, definition in (("password_hash", "VARCHAR(255)"), ("role", "VARCHAR(20) DEFAULT 'student'")):
                    try:
                        conn.execute(text(f"ALTER TABLE students ADD COLUMN {column} {definition}"))
                    except Exception:
                        pass

    @staticmethod
    def _student(row: StudentRecord) -> Student:
        return Student.model_validate({c.name: getattr(row, c.name) for c in StudentRecord.__table__.columns if c.name not in ("password_hash",)})

    async def get_student(self, student_id: str) -> Optional[Student]:
        with self.get_connection() as db:
            row = db.get(StudentRecord, student_id)
            return self._student(row) if row else None

    async def get_student_record(self, student_id: str) -> Optional[StudentRecord]:
        with self.get_connection() as db:
            return db.get(StudentRecord, student_id)

    async def get_transcript(self, student_id: str) -> List[CompletedCourse]:
        with self.get_connection() as db:
            rows = db.scalars(select(CompletedCourseRecord).where(CompletedCourseRecord.student_id == student_id)).all()
            return [CompletedCourse.model_validate(r, from_attributes=True) for r in rows]

    async def get_all_students(self) -> List[Student]:
        with self.get_connection() as db:
            return [self._student(r) for r in db.scalars(select(StudentRecord)).all()]

    async def replace_courses(self, courses: List[Course]) -> None:
        with self.get_connection() as db:
            db.execute(delete(CourseRecord))
            for c in courses:
                db.add(CourseRecord(course_id=c.course_id, name=c.name, credits=c.credits, category=c.category,
                                    suggested_semester=c.suggested_semester, description=c.description))
            db.commit()
            db.execute(text("DELETE FROM course_prerequisites"))
            for c in courses:
                for prerequisite in c.prerequisites:
                    db.execute(text("INSERT INTO course_prerequisites(course_id, prerequisite_id) VALUES (:c, :p)"),
                               {"c": c.course_id, "p": prerequisite})
            db.commit()

    async def seed_curriculum(self, courses: list[dict]) -> None:
        await self.replace_courses([Course(course_id=i["course_id"], name=i.get("name", i.get("course_name")),
            credits=i["credits"], category=i.get("category", "Chuyên ngành"),
            suggested_semester=i.get("suggested_semester", i.get("semester", 1)),
            prerequisites=i.get("prerequisites", []), description=i.get("description")) for i in courses])

    async def create_student_fixture(self, student_id: str, completed_course_ids: list[str]) -> None:
        with self.get_connection() as db:
            row = StudentRecord(student_id=student_id, name="Fixture Student", email=f"{student_id}@example.test",
                major="CNTT", intake_year=2025, current_semester=1, gpa=3, total_credits_completed=0,
                total_credits_required=130, status="active", role="student")
            db.add(row)
            courses = {c.course_id: c for c in db.scalars(select(CourseRecord)).all()}
            for cid in completed_course_ids:
                c = courses[cid]
                row.courses.append(CompletedCourseRecord(course_id=cid, course_name=c.name, credits=c.credits,
                    grade="A", grade_point=4, semester=1))
            db.commit()

    async def get_courses(self) -> List[Course]:
        with self.get_connection() as db:
            rows = db.scalars(select(CourseRecord).order_by(CourseRecord.suggested_semester)).all()
            prereqs = db.execute(text("SELECT course_id, prerequisite_id FROM course_prerequisites")).all()
            by_course = {}
            for course_id, prerequisite_id in prereqs:
                by_course.setdefault(course_id, []).append(prerequisite_id)
            return [Course(course_id=c.course_id, name=c.name, credits=c.credits, category=c.category,
                suggested_semester=c.suggested_semester, description=c.description,
                prerequisites=by_course.get(c.course_id, [])) for c in rows]

db_manager = Database()

from sqlalchemy import ForeignKey, String, Integer, Float, Text, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


course_prerequisites = Table(
    "course_prerequisites", Base.metadata,
    Column("course_id", ForeignKey("courses.course_id", ondelete="CASCADE"), primary_key=True),
    Column("prerequisite_id", ForeignKey("courses.course_id"), primary_key=True),
)


class StudentRecord(Base):
    __tablename__ = "students"
    student_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    major: Mapped[str] = mapped_column(String)
    intake_year: Mapped[int] = mapped_column(Integer)
    current_semester: Mapped[int] = mapped_column(Integer)
    gpa: Mapped[float] = mapped_column(Float)
    total_credits_completed: Mapped[int] = mapped_column(Integer)
    total_credits_required: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="student")
    courses: Mapped[list["CompletedCourseRecord"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class CompletedCourseRecord(Base):
    __tablename__ = "completed_courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.student_id"), index=True)
    course_id: Mapped[str] = mapped_column(String)
    course_name: Mapped[str] = mapped_column(String)
    credits: Mapped[int] = mapped_column(Integer)
    grade: Mapped[str] = mapped_column(String)
    grade_point: Mapped[float] = mapped_column(Float)
    semester: Mapped[int] = mapped_column(Integer)
    student: Mapped[StudentRecord] = relationship(back_populates="courses")


class CourseRecord(Base):
    __tablename__ = "courses"
    course_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    credits: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)
    suggested_semester: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

import argparse, asyncio, json, os, sys
from sqlalchemy import delete
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.database.db import db_manager
from app.models.curriculum import Course
from app.models.orm import StudentRecord, CompletedCourseRecord

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def init_db(students_path="data/students/sample_students.json",
                  curriculum_path="data/curriculum/courses.json", replace=False):
    await db_manager.create_tables()
    path = students_path if os.path.isabs(students_path) else os.path.join(BACKEND_ROOT, students_path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    with db_manager.get_connection() as db:
        if replace:
            db.execute(delete(CompletedCourseRecord))
            db.execute(delete(StudentRecord))
        for item in data:
            row = db.get(StudentRecord, item["student_id"])
            if not row:
                row = StudentRecord(student_id=item["student_id"])
                db.add(row)
            for key in ("name", "email", "major", "intake_year", "current_semester", "gpa",
                        "total_credits_completed", "total_credits_required", "status"):
                setattr(row, key, item[key])
            row.warnings = json.dumps(item.get("warnings", [])) if "warnings" in item else None
            row.role = item.get("role", "student")
            row.password_hash = item.get("password_hash")
            db.query(CompletedCourseRecord).filter_by(student_id=item["student_id"]).delete()
            for c in item.get("completed_courses", []):
                row.courses.append(CompletedCourseRecord(course_id=c["course_id"], course_name=c["course_name"],
                    credits=c["credits"], grade=c["grade"], grade_point=c["grade_point"], semester=c["semester"]))
        db.commit()
    curriculum = curriculum_path if os.path.isabs(curriculum_path) else os.path.join(BACKEND_ROOT, curriculum_path)
    if os.path.exists(curriculum):
        with open(curriculum, encoding="utf-8") as f:
            await db_manager.replace_courses([Course(**item) for item in json.load(f)])
    print(f"Database initialized. Inserted {len(data)} students.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", default="data/students/sample_students.json")
    parser.add_argument("--curriculum", default="data/curriculum/courses.json")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    asyncio.run(init_db(args.students, args.curriculum, args.replace))

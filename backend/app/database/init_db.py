import asyncio
import argparse
import json
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import db_manager
from app.models.curriculum import Course

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def init_db(
    students_path: str = "data/students/sample_students.json",
    curriculum_path: str = "data/curriculum/courses.json",
    replace: bool = False,
):
    print("Creating tables...")
    await db_manager.create_tables()

    json_path = students_path if os.path.isabs(students_path) else os.path.join(BACKEND_ROOT, students_path)
    if not os.path.exists(json_path):
        print(f"Sample data file not found at {json_path}")
        return

    print("Loading sample data...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    async with db_manager.get_connection() as db:
        if replace:
            await db.execute('DELETE FROM completed_courses')
            await db.execute('DELETE FROM students')
        
        students_inserted = 0
        courses_inserted = 0

        for student_data in data:
            warnings = json.dumps(student_data.get('warnings', [])) if 'warnings' in student_data else None
            await db.execute(
                "DELETE FROM completed_courses WHERE student_id = ?",
                (student_data['student_id'],),
            )
            statement = '''
                INSERT OR REPLACE INTO students (
                    student_id, name, email, major, intake_year, current_semester,
                    gpa, total_credits_completed, total_credits_required, status, warnings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            await db.execute(statement, (
                student_data['student_id'], student_data['name'], student_data['email'],
                student_data['major'], student_data['intake_year'], student_data['current_semester'],
                student_data['gpa'], student_data['total_credits_completed'],
                student_data['total_credits_required'], student_data['status'], warnings
            ))
            students_inserted += 1

            if 'completed_courses' in student_data:
                for course in student_data['completed_courses']:
                    await db.execute('''
                        INSERT INTO completed_courses (
                            student_id, course_id, course_name, credits, grade, grade_point, semester
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        student_data['student_id'], course['course_id'], course['course_name'],
                        course['credits'], course['grade'], course['grade_point'], course['semester']
                    ))
                    courses_inserted += 1
                    
        await db.commit()
    curriculum_path = curriculum_path if os.path.isabs(curriculum_path) else os.path.join(BACKEND_ROOT, curriculum_path)
    if os.path.exists(curriculum_path):
        with open(curriculum_path, "r", encoding="utf-8") as f:
            courses = [Course(**item) for item in json.load(f)]
        await db_manager.replace_courses(courses)
        print(f"Loaded {len(courses)} curriculum courses.")
    print(f"Database initialized. Inserted {students_inserted} students and {courses_inserted} courses.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize or update Student Assistant data")
    parser.add_argument("--students", default="data/students/sample_students.json")
    parser.add_argument("--curriculum", default="data/curriculum/courses.json")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing students/transcripts before importing; default is upsert",
    )
    args = parser.parse_args()
    asyncio.run(init_db(args.students, args.curriculum, args.replace))

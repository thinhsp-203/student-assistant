import asyncio
import json
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.db import db_manager

async def init_db():
    print("Creating tables...")
    await db_manager.create_tables()

    json_path = os.path.join("data", "students", "sample_students.json")
    if not os.path.exists(json_path):
        print(f"Sample data file not found at {json_path}")
        return

    print("Loading sample data...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    async with db_manager.get_connection() as db:
        # Clear existing data
        await db.execute('DELETE FROM completed_courses')
        await db.execute('DELETE FROM students')
        
        students_inserted = 0
        courses_inserted = 0

        for student_data in data:
            warnings = json.dumps(student_data.get('warnings', [])) if 'warnings' in student_data else None
            await db.execute('''
                INSERT INTO students (
                    student_id, name, email, major, intake_year, current_semester,
                    gpa, total_credits_completed, total_credits_required, status, warnings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
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
    print(f"Database initialized. Inserted {students_inserted} students and {courses_inserted} courses.")

if __name__ == "__main__":
    asyncio.run(init_db())

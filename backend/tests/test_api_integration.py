import json

from fastapi.testclient import TestClient

from app.dependencies import get_advising_service, get_rag_service, get_student_service
from app.main import app
from app.models.curriculum import Course
from app.models.student import CompletedCourse, Student
from app.schemas.advising import AdvisingResponse


STUDENT = Student(
    student_id="S100",
    name="Nguyen Test",
    email="s100@example.test",
    major="CNTT",
    intake_year=2023,
    current_semester=4,
    gpa=3.4,
    total_credits_completed=45,
    total_credits_required=130,
    status="active",
)
TRANSCRIPT = [
    CompletedCourse(
        course_id="CS101",
        course_name="Programming",
        credits=3,
        grade="A",
        grade_point=4.0,
        semester=1,
    )
]
COURSE = Course(
    course_id="CS201",
    name="Data Structures",
    credits=3,
    category="Cơ sở ngành",
    suggested_semester=2,
    prerequisites=["CS101"],
)


class FakeStudentService:
    async def get_student(self, student_id):
        return STUDENT if student_id == STUDENT.student_id else None

    async def get_transcript(self, student_id):
        return TRANSCRIPT if student_id == STUDENT.student_id else []

    async def get_progress(self, student_id):
        if student_id != STUDENT.student_id:
            return {}
        return {
            "completed_courses": [course.model_dump() for course in TRANSCRIPT],
            "remaining_courses": [COURSE.model_dump()],
            "eligible_courses": [COURSE.model_dump()],
            "completion_percentage": 34.615,
        }


class FakeAdvisingService:
    async def recommend(self, student_id, target_semester=None):
        if student_id != STUDENT.student_id:
            return None
        return AdvisingResponse(
            student_id=student_id,
            current_semester=4,
            target_semester=target_semester or 5,
            eligible_courses=[COURSE],
            blocked_courses=[],
            completed_course_ids=["CS101"],
            recommendation_reasons={"CS201": "Đủ môn tiên quyết."},
            rules=["Loại bỏ môn đã hoàn thành."],
        )


class FakeRagService:
    async def astream_answer(self, question, chat_history=None, student_id=None):
        yield {"sources": [{"content": "Policy", "metadata": {"source": "quy_che_dao_tao.md"}}]}
        yield {"answer": f"Mock answer: {question}", "sources": []}
        yield {"done": True}


def setup_dependencies():
    app.dependency_overrides[get_student_service] = FakeStudentService
    app.dependency_overrides[get_advising_service] = FakeAdvisingService
    app.dependency_overrides[get_rag_service] = FakeRagService


def teardown_dependencies():
    app.dependency_overrides.clear()


def test_student_login_success_and_rejects_unknown_student():
    setup_dependencies()
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/students/login", json={"student_id": "S100"})
            assert response.status_code == 200
            assert response.json()["student"]["student_id"] == "S100"

            response = client.post("/api/v1/students/login", json={"student_id": "missing"})
            assert response.status_code == 401
    finally:
        teardown_dependencies()


def test_transcript_and_progress_use_service_contracts():
    setup_dependencies()
    try:
        with TestClient(app) as client:
            transcript = client.get("/api/v1/students/S100/transcript")
            assert transcript.status_code == 200
            assert transcript.json()["completed_courses"][0]["course_id"] == "CS101"

            progress = client.get("/api/v1/students/S100/progress")
            assert progress.status_code == 200
            assert progress.json()["completed_credits"] == 45
            assert progress.json()["eligible_courses"][0]["course_id"] == "CS201"
    finally:
        teardown_dependencies()


def test_recommendations_use_dependency_override():
    setup_dependencies()
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/advising/S100/recommendations", params={"target_semester": 6}
            )
            assert response.status_code == 200
            body = response.json()
            assert body["target_semester"] == 6
            assert body["eligible_courses"][0]["course_id"] == "CS201"
    finally:
        teardown_dependencies()


def test_chat_sse_streams_mocked_answer_without_llm():
    setup_dependencies()
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/chat/completions",
                json={
                    "message": "Môn nào phù hợp?",
                    "student_id": "S100",
                    "history": [{"role": "user", "content": "Xin chào"}],
                },
            )
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            events = [
                json.loads(line.removeprefix("data: "))
                for line in response.text.splitlines()
                if line.startswith("data: ") and line != "data: [DONE]"
            ]
            assert events[0]["sources"][0]["metadata"]["source"] == "quy_che_dao_tao.md"
            assert events[1]["answer"] == "Mock answer: Môn nào phù hợp?"
            assert "data: [DONE]" in response.text
    finally:
        teardown_dependencies()

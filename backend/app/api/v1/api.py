from fastapi import APIRouter

from app.api.v1.endpoints import chat, students, documents, health, advising

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(advising.router, prefix="/advising", tags=["Academic advising"])

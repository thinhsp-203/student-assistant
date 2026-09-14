from functools import lru_cache

# We will define the services and then provide them here.
# For now, just import the classes (to be created next)
from app.services.chroma_service import ChromaService
from app.services.student_service import StudentService
from app.services.rag_service import RAGService

@lru_cache()
def get_chroma_service() -> ChromaService:
    return ChromaService()

@lru_cache()
def get_student_service() -> StudentService:
    return StudentService()

def get_rag_service() -> RAGService:
    chroma_service = get_chroma_service()
    student_service = get_student_service()
    return RAGService(chroma_service, student_service)

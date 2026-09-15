from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.config import settings
from app.dependencies import get_chroma_service

router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}

@router.get("/detailed")
def health_check_detailed(chroma_service = Depends(get_chroma_service)) -> Dict[str, Any]:
    response = {
        "status": "healthy",
        "version": settings.VERSION,
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "chroma_collection": chroma_service.collection_name,
    }
    try:
        response["document_count"] = chroma_service.get_collection_stats().get("count", 0)
        response["rag_configured"] = bool(settings.GOOGLE_API_KEY)
    except Exception as exc:
        response["status"] = "degraded"
        response["rag_configured"] = False
        response["error"] = str(exc)
    return response

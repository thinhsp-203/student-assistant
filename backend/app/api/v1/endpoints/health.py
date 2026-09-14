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
    stats = chroma_service.get_collection_stats()
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "chroma_collection": chroma_service.collection_name,
        "document_count": stats.get("count", 0)
    }

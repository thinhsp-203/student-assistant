import os
from fastapi import APIRouter, Depends

from app.schemas.document import IngestResponse
from app.services.document_service import DocumentService
from app.dependencies import get_chroma_service

router = APIRouter()

def get_document_service() -> DocumentService:
    return DocumentService()

@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(document_service: DocumentService = Depends(get_document_service)):
    docs_dir = os.path.join(os.getcwd(), "data", "documents")
    if not os.path.exists(docs_dir):
        return {"num_chunks": 0, "collection_name": "academic_kb"}
    
    num_chunks = document_service.ingest_directory(docs_dir)
    return IngestResponse(num_chunks=num_chunks, collection_name="academic_kb")

@router.get("/stats")
def get_stats(chroma_service = Depends(get_chroma_service)):
    return chroma_service.get_collection_stats()

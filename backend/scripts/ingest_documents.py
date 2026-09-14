import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.document_service import DocumentService
from app.services.chroma_service import ChromaService

def ingest():
    print("Initializing ChromaDB...")
    chroma_service = ChromaService()
    chroma_service.initialize()
    
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "documents")
    if not os.path.exists(docs_dir):
        print(f"Documents directory not found at {docs_dir}")
        return

    print("Ingesting documents...")
    doc_service = DocumentService()
    num_chunks = doc_service.ingest_directory(docs_dir)
    print(f"Successfully ingested {num_chunks} chunks into ChromaDB.")

if __name__ == "__main__":
    ingest()

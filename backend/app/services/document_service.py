import os
import re
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.chroma_service import ChromaService
from app.core.config import settings
from app.dependencies import get_chroma_service

class DocumentService:
    def __init__(self):
        self.chroma_service = get_chroma_service()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def ingest_directory(self, dir_path: str) -> int:
        loader = DirectoryLoader(dir_path, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
        docs = loader.load()
        
        for doc in docs:
            filename = os.path.basename(doc.metadata.get("source", ""))
            doc.metadata["doc_type"] = filename
            doc.metadata["institution"] = "HCM-UTE" if "hcmute" in filename.lower() else "demo"
            doc.metadata["source_kind"] = "official_public" if "hcmute" in filename.lower() else "simulated"
            heading = re.search(r"^#\s+(.+)$", doc.page_content, re.MULTILINE)
            source_url = re.search(r"> Nguồn chính thức: \[(https?://[^]]+)\]", doc.page_content)
            if heading:
                doc.metadata["title"] = heading.group(1).strip()
            if source_url:
                doc.metadata["source_url"] = source_url.group(1)
            
        chunks = self.text_splitter.split_documents(docs)
        if chunks:
            self.chroma_service.add_documents(chunks)
        return len(chunks)

    def ingest_file(self, file_path: str) -> int:
        loader = TextLoader(file_path, encoding='utf-8')
        docs = loader.load()
        
        for doc in docs:
            filename = os.path.basename(file_path)
            doc.metadata["doc_type"] = filename
            
        chunks = self.text_splitter.split_documents(docs)
        if chunks:
            self.chroma_service.add_documents(chunks)
        return len(chunks)

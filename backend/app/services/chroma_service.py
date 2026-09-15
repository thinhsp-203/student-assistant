import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from typing import List, Dict, Any, Optional

from app.core.config import settings

class ChromaService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = "academic_kb"
        # Keep application startup usable for health/profile endpoints without
        # requiring an external API key. Embeddings are needed only on RAG use.
        self.embeddings = None
        self.client = None
        self.vectorstore = None

    def initialize(self):
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        if self.embeddings is None and not settings.GOOGLE_API_KEY:
            return
        if self.embeddings is None:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY
            )
        try:
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                collection_metadata={"hnsw:space": "cosine"}
            )
        except Exception as exc:
            raise RuntimeError(
                f"Không thể khởi tạo Chroma với LLM_MODEL={settings.LLM_MODEL} "
                f"và EMBEDDING_MODEL={settings.EMBEDDING_MODEL}: {exc}"
            ) from exc

    def add_documents(self, docs, metadatas=None):
        if not self.vectorstore:
            self.initialize()
        if not self.vectorstore:
            raise RuntimeError("GOOGLE_API_KEY is required to ingest documents")
        return self.vectorstore.add_documents(documents=docs)

    def search(self, query: str, k: int = 5, filter: Optional[Dict[str, Any]] = None):
        if not self.vectorstore:
            self.initialize()
        if not self.vectorstore:
            raise RuntimeError("GOOGLE_API_KEY is required to search documents")
        return self.vectorstore.similarity_search(query, k=k, filter=filter)

    def get_retriever(self, k: int = 5):
        if not self.vectorstore:
            self.initialize()
        if not self.vectorstore:
            raise RuntimeError("GOOGLE_API_KEY is required to retrieve documents")
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

    def delete_collection(self):
        if self.client:
            try:
                self.client.delete_collection(name=self.collection_name)
            except ValueError:
                pass

    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.client:
            self.initialize()
        try:
            collection = self.client.get_collection(self.collection_name)
            return {"count": collection.count()}
        except ValueError:
            return {"count": 0}

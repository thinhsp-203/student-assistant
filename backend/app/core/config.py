from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    GOOGLE_API_KEY: str = ""
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    SQLITE_DATABASE_URL: str = "./data/students.db"
    LLM_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "models/text-embedding-005"
    
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_TOP_K: int = 5
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

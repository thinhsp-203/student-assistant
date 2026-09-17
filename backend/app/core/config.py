from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    SQLITE_DATABASE_URL: str = "./data/students.db"
    DATABASE_URL: str = ""
    JWT_SECRET_KEY: str = "change-this-development-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LLM_MODEL: str = "gemini-3.6-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    
    CHUNK_SIZE: int = 1400
    CHUNK_OVERLAP: int = 150
    RETRIEVAL_TOP_K: int = 5
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def google_api_key(self) -> str:
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY

    @property
    def database_url(self) -> str:
        url = self.DATABASE_URL.strip()
        if url:
            return url
        return f"sqlite:///{self.SQLITE_DATABASE_URL}"

settings = Settings()

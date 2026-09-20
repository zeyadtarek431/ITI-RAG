import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG-Powered Document Assistant API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    
    # Vector Database Config
    PERSIST_DIRECTORY: str = os.getenv("PERSIST_DIRECTORY", "./data/vector_store")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "rag_documents")
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "3"))

    # LLM Config
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # CORS Config
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "*"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

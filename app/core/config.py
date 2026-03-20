import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    VECTOR_DB_PATH: str = os.path.join(BASE_DIR, "vector_store")
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CACHE_DIR: str = os.path.join(BASE_DIR, "cache")
    UPLOADS_DIR: str = os.path.join(BASE_DIR, "data", "uploads")

settings = Settings()
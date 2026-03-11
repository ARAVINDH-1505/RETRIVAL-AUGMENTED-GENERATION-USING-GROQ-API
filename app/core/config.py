import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    VECTOR_DB_PATH = "vector_store"

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

settings = Settings()
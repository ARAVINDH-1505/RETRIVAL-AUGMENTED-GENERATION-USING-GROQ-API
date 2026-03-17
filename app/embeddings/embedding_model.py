from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings

_embedding_instance = None

def load_embedding_model():
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
    return _embedding_instance
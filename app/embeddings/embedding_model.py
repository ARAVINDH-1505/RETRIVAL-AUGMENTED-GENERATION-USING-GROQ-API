from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings
from app.core.logging import logger

_embedding_instance = None

def load_embedding_model():
    global _embedding_instance
    if _embedding_instance is None:
        try:
            logger.info(f"Attempting to load embedding model '{settings.EMBEDDING_MODEL}' from local cache...")
            _embedding_instance = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL,
                model_kwargs={"local_files_only": True}
            )
            logger.info("Successfully loaded embedding model from local cache.")
        except Exception as e:
            logger.warning(f"Could not load embedding model locally: {e}. Falling back to Hugging Face Hub download...")
            _embedding_instance = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )
            logger.info("Successfully loaded embedding model from Hugging Face Hub.")
    return _embedding_instance
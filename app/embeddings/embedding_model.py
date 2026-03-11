from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings


def load_embedding_model():

    embedding = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )

    return embedding
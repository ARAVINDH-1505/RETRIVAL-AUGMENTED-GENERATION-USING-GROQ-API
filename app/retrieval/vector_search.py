import os
import asyncio
from langchain_community.vectorstores import FAISS
from app.embeddings.embedding_model import load_embedding_model
from app.core.config import settings
from app.core.logging import logger

db = None

def load_vector_store():
    global db
    if db is None:
        if not os.path.exists(settings.VECTOR_DB_PATH) or not os.listdir(settings.VECTOR_DB_PATH):
            logger.warning(f"Vector DB path {settings.VECTOR_DB_PATH} is empty or does not exist.")
            return None

        embedding = load_embedding_model()
        db = FAISS.load_local(
            settings.VECTOR_DB_PATH,
            embedding,
            allow_dangerous_deserialization=True
        )
        logger.info("Loaded FAISS vector store into memory.")
    return db

async def vector_search_async(query, k=10):
    def sync_search():
        db_instance = load_vector_store()
        if db_instance is None:
            return []
        return db_instance.similarity_search(query, k=k)

    return await asyncio.to_thread(sync_search)
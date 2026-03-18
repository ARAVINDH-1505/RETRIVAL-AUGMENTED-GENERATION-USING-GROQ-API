from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.database.db import create_tables
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing AI models on startup to reduce first-query latency...")
    from app.embeddings.embedding_model import load_embedding_model
    from app.reranker.cross_encoder import get_reranker
    from app.retrieval.vector_search import load_vector_store
    
    import asyncio
    # Preload the HuggingFace singletons into memory securely before API binds
    await asyncio.to_thread(load_embedding_model)
    await asyncio.to_thread(get_reranker)
    await asyncio.to_thread(load_vector_store)
    
    logger.info("AI Models initialized successfully. API is ready.")
    yield
    
    # Teardown: clear the disk cache when the server stops
    logger.info("Server shutting down. Clearing query cache to prevent stale answers...")
    import shutil
    import os
    if os.path.exists("./cache"):
        try:
            shutil.rmtree("./cache")
            logger.info("Cache successfully cleared.")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

create_tables()

app = FastAPI(
    title="Production Hybrid RAG System",
    lifespan=lifespan
)

app.include_router(router)
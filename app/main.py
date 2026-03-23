from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.database.db import create_tables
from app.core.logging import logger
import os

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
    from app.core.config import settings
    if os.path.exists(settings.CACHE_DIR):
        try:
            shutil.rmtree(settings.CACHE_DIR)
            logger.info("Cache successfully cleared.")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

create_tables()

app = FastAPI(
    title="Production Hybrid RAG System",
    lifespan=lifespan
)

# API routes mounted at /api namespace in UI context, but currently they are at root.
# Let's include router at /api to avoid conflicts.
app.include_router(router, prefix="/api")

# Ensure static folder exists
os.makedirs("app/static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("app/static/index.html")
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Production Hybrid RAG System"
)

app.include_router(router)
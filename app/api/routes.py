from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.pipeline import rag_pipeline

router = APIRouter()

class QueryRequest(BaseModel):

    input1: str
    
@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/query")
async def query(request: QueryRequest):

    result = rag_pipeline(request.input1)

    return {"answer": result}
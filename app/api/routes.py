from fastapi import UploadFile, File
import shutil
import os

from app.ingestion.upload_pipeline import process_uploaded_document

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

@router.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):

    file_path = os.path.join("data/uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    process_uploaded_document(file_path)

    return {
        "message": "Document uploaded and indexed",
        "filename": file.filename
    }
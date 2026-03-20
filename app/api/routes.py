from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
import shutil
import os
import time

from app.ingestion.upload_pipeline import process_uploaded_document
from app.rag.langgraph_flow import build_graph
from app.database.db import get_db_connection
from app.utils.cache import get_cache, set_cache

router = APIRouter()
rag_graph = build_graph()

class QueryRequest(BaseModel):
    input1: str

@router.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}
    
@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/query")
async def query(request: QueryRequest):
    query_text = request.input1
    start_total = time.time()
    
    cached = get_cache(query_text)
    if cached:
        return {"answer": cached, "cached": True, "sources": []}

    # Run LangGraph flow asynchronously
    result = await rag_graph.ainvoke({"original_query": query_text, "timing": {}})
    
    docs = result.get("documents", [])
    answer = result.get("answer", "")
    timing = result.get("timing", {})
    
    set_cache(query_text, answer)
    
    timing["total_time"] = round(time.time() - start_total, 3)
    
    return {
        "answer": answer,
        "sources": [
            {
                "document": doc.metadata.get("doc_name", "Unknown"),
                "chunk": doc.metadata.get("chunk_id", "Unknown")
            }
            for doc in docs
        ],
        "timing": timing
    }

def bg_process_upload(file_path: str, filename: str):
    try:
        process_uploaded_document(file_path, filename)
    except Exception as e:
        import traceback
        from app.core.logging import logger
        logger.error(f"Background upload failed for {filename}: {str(e)}")
        logger.error(traceback.format_exc())

@router.post("/upload_document")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    from app.core.config import settings
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOADS_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Offload processing to background task so API responds immediately
    background_tasks.add_task(bg_process_upload, file_path, file.filename)

    return {"message": "Document upload accepted and indexing started in background."}

@router.get("/documents")
def list_documents():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        
    return [{"id": r[0], "filename": r[1], "file_hash": r[2], "upload_time": r[3]} for r in rows]

@router.delete("/document/{doc_id}")
def delete_document(doc_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id=?", (doc_id,))
        conn.commit()

    return {"message": "Document deleted"}
import uuid
from datetime import datetime

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

from app.ingestion.splitter import split_documents
from app.embeddings.embedding_model import load_embedding_model
from app.database.db import get_db_connection
from app.utils.hash_utils import generate_file_hash
import app.retrieval.vector_search as vs
from app.core.logging import logger

VECTOR_STORE_PATH = "vector_store"


def process_uploaded_document(file_path, filename):

    file_hash = generate_file_hash(file_path)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM documents WHERE file_hash=?",
            (file_hash,)
        )
        exists = cursor.fetchone()

        if exists:
            logger.info(f"Document {filename} already uploaded.")
            return {"message": "Document already uploaded"}

    doc_id = str(uuid.uuid4())

    loader = PyPDFLoader(file_path)

    docs = loader.load()

    chunks = split_documents(docs, filename)

    logger.info(f"Created {len(chunks)} chunks for document {filename}")

    embedding = load_embedding_model()

    db = FAISS.load_local(
        VECTOR_STORE_PATH,
        embedding,
        allow_dangerous_deserialization=True
    )

    for i, chunk in enumerate(chunks):

        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["doc_name"] = filename
        chunk.metadata["chunk_id"] = i

    db.add_documents(chunks)

    db.save_local(VECTOR_STORE_PATH)
    vs.db = None
    
    # Also invalidate BM25 cache if it exists
    import app.retrieval.bm25 as bm25
    bm25._bm25_cache = None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?)",
            (doc_id, filename, file_hash, str(datetime.utcnow()))
        )
        conn.commit()

    logger.info(f"Document {filename} successfully indexed.")
    return {"message": "Document indexed", "doc_id": doc_id}
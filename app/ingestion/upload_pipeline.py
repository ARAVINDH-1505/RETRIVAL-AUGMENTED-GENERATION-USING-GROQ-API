import uuid
from datetime import datetime

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

from app.ingestion.splitter import split_documents
from app.embeddings.embedding_model import load_embedding_model
from app.database.db import get_connection
from app.utils.hash_utils import generate_file_hash


VECTOR_STORE_PATH = "vector_store"


def process_uploaded_document(file_path, filename):

    file_hash = generate_file_hash(file_path)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM documents WHERE file_hash=?",
        (file_hash,)
    )

    exists = cursor.fetchone()

    if exists:
        conn.close()
        return {"message": "Document already uploaded"}

    doc_id = str(uuid.uuid4())

    loader = PyPDFLoader(file_path)

    docs = loader.load()

    chunks = split_documents(docs, filename)

    embedding = load_embedding_model()

    db = FAISS.load_local(
        VECTOR_STORE_PATH,
        embedding,
        allow_dangerous_deserialization=True
    )

    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id

    db.add_documents(chunks)

    db.save_local(VECTOR_STORE_PATH)

    cursor.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?)",
        (
            doc_id,
            filename,
            file_hash,
            str(datetime.utcnow())
        )
    )

    conn.commit()
    conn.close()

    return {"message": "Document indexed", "doc_id": doc_id}
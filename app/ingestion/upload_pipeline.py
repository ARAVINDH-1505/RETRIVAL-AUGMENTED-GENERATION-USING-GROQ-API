from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

from app.ingestion.splitter import split_documents
from app.embeddings.embedding_model import load_embedding_model


VECTOR_STORE_PATH = "vector_store"


def process_uploaded_document(file_path):

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    chunks = split_documents(docs)

    embedding = load_embedding_model()

    db = FAISS.load_local(
        VECTOR_STORE_PATH,
        embedding,
        allow_dangerous_deserialization=True
    )

    db.add_documents(chunks)

    db.save_local(VECTOR_STORE_PATH)
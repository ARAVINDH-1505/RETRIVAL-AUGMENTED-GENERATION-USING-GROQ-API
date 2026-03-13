from app.ingestion.loader import load_documents
from app.ingestion.splitter import split_documents
from app.embeddings.embedding_model import load_embedding_model
from langchain_community.vectorstores import FAISS

docs = load_documents()

chunks = split_documents(docs)

embedding = load_embedding_model()

db = FAISS.from_documents(chunks, embedding)

db.save_local("vector_store")

print("Vector store created successfully")
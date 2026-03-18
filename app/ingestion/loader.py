from langchain_community.document_loaders import PyPDFLoader
import os
import logging
from app.core.logging import logger

def load_documents():
    path = "data/documents"
    
    if not os.path.exists(path):
        logger.warning(f"Directory {path} does not exist. Creating it.")
        os.makedirs(path, exist_ok=True)
        return []

    documents = []

    for file in os.listdir(path):
        if file.endswith(".pdf"):
            file_path = os.path.join(path, file)
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Successfully loaded {file_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    return documents
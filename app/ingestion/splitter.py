from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def split_documents(docs, filename=None):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120
    )

    chunks = splitter.split_documents(docs)

    for i, chunk in enumerate(chunks):
        # Fall back to using the native source from PyPDFLoader if filename isn't explicitly provided
        doc_name = filename if filename else os.path.basename(chunk.metadata.get("source", "Unknown"))
        
        chunk.metadata["doc_name"] = doc_name
        chunk.metadata["chunk_id"] = i

    return chunks
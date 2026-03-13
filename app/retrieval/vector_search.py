from langchain_community.vectorstores import FAISS
from app.embeddings.embedding_model import load_embedding_model
from app.core.config import settings

def load_vector_store():

    embedding = load_embedding_model()

    deb = FAISS.load_local(
        settings.VECTOR_DB_PATH,
        embedding,
        allow_dangerous_deserialization=True
    )

    return deb

db = load_vector_store()
def vector_search(query):

    

    docs = db.similarity_search(query, k=10)

    return docs
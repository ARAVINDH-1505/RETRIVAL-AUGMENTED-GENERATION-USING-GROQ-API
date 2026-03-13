from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from app.retrieval.vector_search import load_vector_store

# Load documents already stored in FAISS
db = load_vector_store()

documents = db.docstore._dict

texts = [doc.page_content for doc in documents.values()]

tokenized = [text.split() for text in texts]

bm25 = BM25Okapi(tokenized)


def bm25_search(query, k=10):

    tokens = query.split()

    scores = bm25.get_scores(tokens)

    ranked = sorted(
        zip(scores, texts),
        reverse=True
    )[:k]

    results = []

    for score, text in ranked:
        results.append(
            Document(page_content=text)
        )

    return results
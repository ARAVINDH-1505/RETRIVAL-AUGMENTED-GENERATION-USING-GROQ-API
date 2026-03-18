import asyncio
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from app.retrieval.vector_search import load_vector_store
from app.core.logging import logger

_bm25_cache = None

def get_bm25_index():
    global _bm25_cache
    if _bm25_cache is not None:
        return _bm25_cache

    logger.info("Building BM25 index from FAISS docstore...")
    db = load_vector_store()
    
    if not db or not db.docstore._dict:
        logger.warning("Vector store is empty, returning empty BM25 cache.")
        return None, [], []

    documents = db.docstore._dict
    texts = []
    metadata = []
    
    for doc in documents.values():
        texts.append(doc.page_content)
        metadata.append(doc.metadata)

    tokenized = [text.split() for text in texts]
    bm25 = BM25Okapi(tokenized)
    
    _bm25_cache = (bm25, texts, metadata)
    return _bm25_cache


async def bm25_search_async(query, k=10):
    def sync_search():
        index_data = get_bm25_index()
        if index_data is None or len(index_data) != 3:
            return []
            
        bm25, texts, metadata = index_data
        if not bm25:
            return []

        scores = bm25.get_scores(query.split())
        ranked = sorted(
            zip(scores, texts, metadata),
            key=lambda x: x[0],
            reverse=True
        )[:k]

        return [Document(page_content=text, metadata=meta) for score, text, meta in ranked]

    return await asyncio.to_thread(sync_search)
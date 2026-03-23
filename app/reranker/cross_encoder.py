import asyncio
from sentence_transformers import CrossEncoder

model = None

def get_reranker():
    global model
    if model is None:
        try:
            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", local_files_only=True)
        except Exception:
            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return model

async def rerank_async(query, documents):
    if not documents:
        return []

    def sync_rerank():
        encoder = get_reranker()
        pairs = [(query, doc.page_content) for doc in documents]
        scores = encoder.predict(pairs)
        ranked = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True
        )
        return [doc for score, doc in ranked[:5]]

    return await asyncio.to_thread(sync_rerank)
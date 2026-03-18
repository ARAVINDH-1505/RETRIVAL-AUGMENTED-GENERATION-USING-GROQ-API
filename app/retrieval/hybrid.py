import asyncio
from .vector_search import vector_search_async
from .bm25 import bm25_search_async

async def hybrid_search_async(query):
    # Run both searches concurrently
    vector_results, bm25_results = await asyncio.gather(
        vector_search_async(query),
        bm25_search_async(query)
    )

    combined = vector_results + bm25_results
    
    seen = set()
    unique_docs = []

    for doc in combined:
        text = doc.page_content
        if text not in seen:
            seen.add(text)
            unique_docs.append(doc)

    return unique_docs
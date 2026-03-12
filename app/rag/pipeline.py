import time

from app.query.rewrite import rewrite_query
from app.retrieval.hybrid import hybrid_search
from app.reranker.cross_encoder import rerank
from app.generation.llm import generate_answer
from app.utils.cache import get_cache, set_cache


def rag_pipeline(query):

    start_total = time.time()

    cached = get_cache(query)
    if cached:
        return {"answer": cached, "cached": True}

    # -------------------
    # Query Rewriting
    # -------------------
    t1 = time.time()
    rewritten = rewrite_query(query)
    t2 = time.time()

    # -------------------
    # Retrieval
    # -------------------
    t3 = time.time()
    docs = hybrid_search(rewritten)
    t4 = time.time()

    # -------------------
    # Re-ranking
    # -------------------
    t5 = time.time()
    ranked_docs = rerank(rewritten, docs)
    t6 = time.time()

    context = "\n".join(
        [doc.page_content for doc in ranked_docs]
    )

    # -------------------
    # Generation
    # -------------------
    t7 = time.time()
    answer = generate_answer(context, query)
    t8 = time.time()

    total_time = time.time() - start_total

    set_cache(query, answer)

    return {
        "answer": answer,
        "timing": {
            "query_rewrite": round(t2 - t1, 3),
            "retrieval": round(t4 - t3, 3),
            "reranking": round(t6 - t5, 3),
            "generation": round(t8 - t7, 3),
            "total_time": round(total_time, 3)
        }
    }
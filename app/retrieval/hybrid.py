from .vector_search import vector_search
from .bm25 import bm25_search


def hybrid_search(query):

    vector_results = vector_search(query)

    bm25_results = bm25_search(query)

    combined = []

    # add vector docs
    for doc in vector_results:
        combined.append(doc)

    # add bm25 docs
    for doc in bm25_results:
        combined.append(doc)

    return combined
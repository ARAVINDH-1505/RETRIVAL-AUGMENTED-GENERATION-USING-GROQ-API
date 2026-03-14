from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

def rerank(query, documents):

    pairs = [(query, doc.page_content) for doc in documents]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(scores, documents),
        key=lambda x: x[0],
        reverse=True
    )

    return [doc for score, doc in ranked[:5]]
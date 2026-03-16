from langchain_groq import ChatGroq
from app.core.config import settings


def generate_queries(query):

    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )

    prompt = f"""
Generate 3 different search queries related to this question.

Question:
{query}

Queries:
"""

    response = llm.invoke(prompt)

    queries = response.content.split("\n")

    queries = [q.strip("- ").strip() for q in queries if q.strip()]

    queries.append(query)

    return queries
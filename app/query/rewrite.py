from langchain_groq import ChatGroq
from app.core.config import settings

async def rewrite_query_async(query):
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant"
    )

    prompt = f"""
Rewrite this search query to improve retrieval.

Query:
{query}
"""

    response = await llm.ainvoke(prompt)
    return response.content
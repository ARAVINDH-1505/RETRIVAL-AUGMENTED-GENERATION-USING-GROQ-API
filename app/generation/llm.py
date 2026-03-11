from langchain_groq import ChatGroq
from app.core.config import settings

def generate_answer(context, query):

    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )

    prompt = f"""
Answer using the provided context.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    return response.content
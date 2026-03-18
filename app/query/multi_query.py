from langchain_groq import ChatGroq
from app.core.config import settings

async def generate_queries_async(query):
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )

    prompt = f"""
You are an AI search assistant. Your task is to generate 3 optimized search queries based on the user's question to retrieve the best documents from a vector database.

CRITICAL INSTRUCTIONS:
1. If the user's question contains multiple distinct topics (e.g. "What is Machine Learning and what is a Linked List?"), you MUST split them into separate, independent queries. Do NOT combine unrelated topics into a single query.
2. Make the queries specific, using important keywords from the original question.
3. Output EXACTLY 3 queries, one per line, with no bullet points, numbers, or introductory text.

Question:
{query}
"""

    response = await llm.ainvoke(prompt)
    
    # Clean up the output to ensure we just get the strings
    queries = []
    for line in response.content.split("\n"):
        cleaned = line.strip("-*1234567890. ")
        if cleaned:
            queries.append(cleaned)
            
    # Keep only the top 3 generated queries to maintain performance
    queries = queries[:3]
    queries.append(query)
    
    return queries
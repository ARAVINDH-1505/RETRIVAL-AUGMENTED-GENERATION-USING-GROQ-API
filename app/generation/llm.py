from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

async def generate_answer_async(context, query):
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.1
    )

    system_prompt = """You are a helpful, knowledgeable AI assistant. Your goal is to answer the user's question using ONLY the provided Context.

CRITICAL RULES:
1. You are FORBIDDEN from using your own general training knowledge. You MUST rely exclusively on the Context.
2. If the user asks a multi-part question, and the Context only contains information for one part, provide the answer for the part you have, and explicitly mention that the other part is missing from the provided documents.
3. Even if the Context only provides partial or loosely related information to the question, you should synthesize whatever useful information you can find from it to help the user.
4. If the Context DOES NOT contain ANY explicitly relevant information at all, you MUST reply with EXACTLY this string and absolutely nothing else:
"I'm sorry, but that information is not available in the provided documents."

Context:
{context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({"context": context, "query": query})
    
    return response.content
import operator
import time
from typing import Annotated, TypedDict, Sequence
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END

from app.query.rewrite import rewrite_query_async
from app.query.multi_query import generate_queries_async
from app.retrieval.hybrid import hybrid_search_async
from app.reranker.cross_encoder import rerank_async
from app.generation.llm import generate_answer_async
from app.core.logging import logger

class GraphState(TypedDict):
    original_query: str
    rewritten_query: str
    multi_queries: list[str]
    documents: list[Document]
    answer: str
    timing: dict

async def rewrite_node(state: GraphState):
    start_time = time.time()
    query = state["original_query"]
    logger.info(f"Rewriting query: {query}")
    rewritten = await rewrite_query_async(query)
    
    timing = state.get("timing", {})
    timing["rewrite_time"] = round(time.time() - start_time, 3)
    return {"rewritten_query": rewritten, "timing": timing}

async def retrieve_node(state: GraphState):
    start_time = time.time()
    query = state["rewritten_query"]
    logger.info("Generating multi-queries and retrieving documents")
    queries = await generate_queries_async(query)
    
    all_docs = []
    # Could use asyncio.gather here, but sequential is fine for list comprehension if inside a task loop,
    # however we will keep it simple and just await in loop since hybrid search is fast enough now.
    for q in queries:
        docs = await hybrid_search_async(q)
        all_docs.extend(docs)

    seen = set()
    unique_docs = []
    for doc in all_docs:
        text = doc.page_content
        if text not in seen:
            seen.add(text)
            unique_docs.append(doc)
            
    timing = state.get("timing", {})
    timing["retrieval_time"] = round(time.time() - start_time, 3)
    # Keep top 15 for reranking to reduce time
    return {"multi_queries": queries, "documents": unique_docs[:15], "timing": timing}

async def rerank_node(state: GraphState):
    start_time = time.time()
    query = state["original_query"]
    docs = state["documents"]
    logger.info(f"Reranking {len(docs)} documents")
    ranked = await rerank_async(query, docs)
    
    timing = state.get("timing", {})
    timing["rerank_time"] = round(time.time() - start_time, 3)
    return {"documents": ranked[:4], "timing": timing}  # Keep top 4

async def generate_node(state: GraphState):
    start_time = time.time()
    query = state["original_query"]
    docs = state["documents"]
    
    context = ""
    for doc in docs:
        source = doc.metadata.get("doc_name", "Unknown")
        chunk = doc.metadata.get("chunk_id", "Unknown")
        context += f"Source Document: {source}\nChunk Number: {chunk}\n{doc.page_content}\n-------------------\n"
        
    logger.info("Generating final answer")
    answer = await generate_answer_async(context, query)
    
    timing = state.get("timing", {})
    timing["generation_time"] = round(time.time() - start_time, 3)
    return {"answer": answer, "timing": timing}

def build_graph():
    graph = StateGraph(GraphState)
    
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("generate", generate_node)
    
    graph.set_entry_point("rewrite")
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", END)
    
    return graph.compile()
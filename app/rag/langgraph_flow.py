from langgraph.graph import StateGraph

def build_graph():

    graph = StateGraph()

    graph.add_node("rewrite")
    graph.add_node("retrieve")
    graph.add_node("rerank")
    graph.add_node("generate")

    graph.set_entry_point("rewrite")

    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")

    return graph.compile()
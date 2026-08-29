from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import ChatState
from nodes import chat_node


# ---------------- CHECKPOINTER ----------------

checkpointer = MemorySaver()


# ---------------- GRAPH ----------------

graph = StateGraph(ChatState)


graph.add_node(
    "chat_node",
    chat_node
)


graph.add_edge(
    START,
    "chat_node"
)


graph.add_edge(
    "chat_node",
    END
)


# ---------------- COMPILE GRAPH ----------------

chatbot_graph = graph.compile(
    checkpointer=checkpointer
)
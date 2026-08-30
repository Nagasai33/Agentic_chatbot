import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from state import ChatState
from nodes import chat_node


# ---------------- SQLITE CHECKPOINTER ----------------

conn = sqlite3.connect(
    "chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)


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
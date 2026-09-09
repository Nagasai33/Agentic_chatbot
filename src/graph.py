import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

from state import ChatState
from nodes import chat_node, tools



conn = sqlite3.connect("chatbot.db", check_same_thread=False)

checkpointer = SqliteSaver(conn)


graph = StateGraph(ChatState)

# Agent node
graph.add_node("chat_node", chat_node)

# Tool execution node
graph.add_node("tools", ToolNode(tools))


# Start → Agent
graph.add_edge(START, "chat_node")

# Agent decides:
#   tool call → tools
#   normal answer → END
graph.add_conditional_edges(
    "chat_node",
    tools_condition
)

# After tool execution → Agent again
graph.add_edge("tools", "chat_node")


chatbot_graph = graph.compile(
    checkpointer=checkpointer
)
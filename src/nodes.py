from state import ChatState
from llm import llm


def chat_node(state: ChatState):

    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }
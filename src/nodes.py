from state import ChatState
from llm import llm
from tools.calculator import calculator


tools = [
    calculator,
]


llm_with_tools = llm.bind_tools(tools)


def chat_node(state: ChatState):
    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}
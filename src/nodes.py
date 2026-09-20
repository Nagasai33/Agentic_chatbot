from state import ChatState
from llm import llm
from tools.calculator import calculator
from langchain_core.messages import SystemMessage

MAX_HISTORY_MESSAGES = 10
MAX_HISTORY_TOKENS = 2000


def estimate_message_tokens(message):
    content = getattr(message, "content", "")

    if not isinstance(content, str):
        content = str(content)

    return max(1, len(content) // 4)

def get_recent_messages(messages):
    recent_messages = messages[-MAX_HISTORY_MESSAGES:]

    # If the first message in our window is a tool message,
    # remove it so we don't start with an incomplete tool interaction.
    while recent_messages and recent_messages[0].type == "tool":
        recent_messages = recent_messages[1:]

    return recent_messages


tools = [
    calculator,
]


llm_with_tools = llm.bind_tools(tools)


def chat_node(state: ChatState):

    messages = get_recent_messages(state["messages"])

    system_message = SystemMessage(
        content="""
You are a helpful AI assistant.

When you use the calculator tool, present the final calculation result
in a simple and user-friendly format.

For simple calculations:
- Give the final answer clearly.
- Avoid unnecessary LaTeX formatting.
- Avoid unnecessary calculation steps.
- Use normal mathematical symbols when useful.
- Do not add unnecessary parentheses.
- Keep simple calculation answers concise.

Examples:

User: Calculate 25 * 45
Good response: 25 × 45 = 1125

User: Calculate (10 + 20) * 5
Good response: (10 + 20) × 5 = 150

User: Calculate 1 + 2 + 3 + 4 + 5
Good response: 1 + 2 + 3 + 4 + 5 = 15
"""
    )

    messages_with_system = [system_message] + messages

    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
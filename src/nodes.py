from state import ChatState
from llm import llm
from tools.calculator import calculator
from tools.web_search import web_search
from langchain_core.messages import SystemMessage

MAX_HISTORY_MESSAGES = 10
MAX_HISTORY_TOKENS = 4000


def estimate_message_tokens(message):
    content = getattr(message, "content", "")

    if not isinstance(content, str):
        content = str(content)

    return max(1, len(content) // 4)

def get_recent_messages(messages):
    selected_messages = []
    total_tokens = 0

    # Start from the newest message
    for message in reversed(messages):

        message_tokens = estimate_message_tokens(message)

        # Don't exceed the history token budget
        if total_tokens + message_tokens > MAX_HISTORY_TOKENS:
            break

        selected_messages.append(message)
        total_tokens += message_tokens

        # Also respect the message-count limit
        if len(selected_messages) >= MAX_HISTORY_MESSAGES:
            break

    # Restore the original conversation order
    selected_messages.reverse()

    # Don't start with an orphaned tool result
    while selected_messages and selected_messages[0].type == "tool":
        selected_messages.pop(0)

    return selected_messages


tools = [
    calculator,
    web_search,
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


Web search instructions:

- You have access to a web search tool.
- Use the web search tool when the user asks for current, recent, latest, today's, or time-sensitive information.
- Use the web search tool when the user asks about events or developments after your knowledge cutoff.
- Do not claim that you cannot provide current information when the web search tool can find it.
- After receiving web search results, use those results to answer the user's question clearly.
- Do not show the raw tool output to the user.
- If the user asks a simple general question that does not require current information, you can answer directly without web search.
"""
    )

    messages_with_system = [system_message] + messages

    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
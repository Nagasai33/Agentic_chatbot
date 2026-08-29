import streamlit as st

from threads import (
    chatbot,
    create_thread,
    get_thread_messages
)


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Agentic Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ---------------- SESSION STATE ----------------

# Store all chat threads
if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = []


# Create first thread
if "current_thread_id" not in st.session_state:

    thread_id = create_thread()

    st.session_state.current_thread_id = thread_id

    st.session_state.chat_threads.append(
        {
            "id": thread_id,
            "title": "New Chat"
        }
    )


# ---------------- HELPER FUNCTIONS ----------------

def create_new_chat():

    thread_id = create_thread()

    st.session_state.chat_threads.append(
        {
            "id": thread_id,
            "title": "New Chat"
        }
    )

    st.session_state.current_thread_id = thread_id


def switch_chat(thread_id):

    st.session_state.current_thread_id = thread_id


def get_current_messages():

    return get_thread_messages(
        st.session_state.current_thread_id
    )


# ---------------- SIDEBAR ----------------

with st.sidebar:

    # New Chat
    if st.button(
        "＋ New chat",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()


    st.divider()


    # Recent chats
    st.caption("Recent")


    for chat in reversed(
        st.session_state.chat_threads
    ):

        thread_id = chat["id"]
        title = chat["title"]


        if st.button(
            f"💬 {title}",
            key=f"chat_{thread_id}",
            use_container_width=True
        ):

            switch_chat(thread_id)

            st.rerun()


    # Push settings to bottom
    st.markdown(
        """
        <div style="height: 55vh;"></div>
        """,
        unsafe_allow_html=True
    )


    st.divider()

    st.write("⚙️ Settings")
    st.write("👤 Profile")


# ---------------- MAIN CHAT ----------------

st.title("🤖 Agentic Chatbot")


# Current thread
current_thread_id = (
    st.session_state.current_thread_id
)


# Get messages for current thread
messages = get_current_messages()


# ---------------- DISPLAY MESSAGES ----------------

for message in messages:

    if message.type == "human":

        role = "user"

    elif message.type == "ai":

        role = "assistant"

    else:

        continue


    with st.chat_message(role):

        st.markdown(message.content)


# ---------------- CHAT INPUT ----------------

user_input = st.chat_input(
    "Ask me anything..."
)


# ---------------- HANDLE MESSAGE ----------------

if user_input:

    # Find current chat
    current_chat = next(
        chat
        for chat in st.session_state.chat_threads
        if chat["id"] == current_thread_id
    )


    # Create title from first message
    if current_chat["title"] == "New Chat":

        current_chat["title"] = user_input[:30]

        if len(user_input) > 30:

            current_chat["title"] += "..."


    # Send message to LangGraph
    response = chatbot(
        user_input,
        current_thread_id
    )


    # Refresh UI
    st.rerun()
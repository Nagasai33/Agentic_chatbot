import streamlit as st

from threads import (
    chatbot,
    create_thread,
    get_all_threads,
    get_thread_messages
)


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Agentic Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ---------------- SESSION STATE ----------------

if "chat_threads" not in st.session_state:

    saved_threads = get_all_threads()

    st.session_state.chat_threads = []

    for thread_id in saved_threads:

        messages = get_thread_messages(thread_id)

        title = "New Chat"

        for message in messages:

            if message.type == "human":

                title = message.content[:30]

                if len(message.content) > 30:
                    title += "..."

                break

        st.session_state.chat_threads.append(
            {
                "id": thread_id,
                "title": title
            }
        )


# Create first thread if no saved threads exist
if "current_thread_id" not in st.session_state:

    if st.session_state.chat_threads:

        st.session_state.current_thread_id = (
            st.session_state.chat_threads[0]["id"]
        )

    else:

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

    if st.button(
        "＋ New chat",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()

    st.divider()

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


current_thread_id = (
    st.session_state.current_thread_id
)


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

    current_chat = next(
        chat
        for chat in st.session_state.chat_threads
        if chat["id"] == current_thread_id
    )

    if current_chat["title"] == "New Chat":

        current_chat["title"] = user_input[:30]

        if len(user_input) > 30:
            current_chat["title"] += "..."

    response = chatbot(
        user_input,
        current_thread_id
    )

    st.rerun()
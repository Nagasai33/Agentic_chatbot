import streamlit as st

from threads import (
    stream_chatbot,
    create_thread,
    get_all_chats,
    get_thread_messages,
    update_chat,
    archive_chat
    
)


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Agentic Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ---------------- SESSION STATE ----------------

# Track which chat is currently being edited.
# Initially, no chat is being edited.
if "editing_thread_id" not in st.session_state:
    st.session_state.editing_thread_id = None

if "chat_threads" not in st.session_state:

    st.session_state.chat_threads = get_all_chats()


# Create first thread if no chats exist
if "current_thread_id" not in st.session_state:

    if st.session_state.chat_threads:

        st.session_state.current_thread_id = (
            st.session_state.chat_threads[0]["id"]
        )

    else:

        thread_id = create_thread()

        st.session_state.chat_threads = get_all_chats()

        st.session_state.current_thread_id = thread_id


# ---------------- HELPER FUNCTIONS ----------------

def create_new_chat():

    thread_id = create_thread()

    st.session_state.chat_threads = get_all_chats()

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

    # Always get latest chat metadata from database
    st.session_state.chat_threads = get_all_chats()

    for chat in st.session_state.chat_threads:

        thread_id = chat["id"]
        title = chat["title"]

        # ---------------- EDIT MODE ----------------

        if st.session_state.editing_thread_id == thread_id:

            new_title = st.text_input(
                "Chat title",
                value=title,
                key=f"edit_input_{thread_id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "💾 Save",
                    key=f"save_{thread_id}",
                    use_container_width=True
                ):

                    if new_title.strip():

                        update_chat(
                            thread_id,
                            title=new_title.strip()
                        )

                    st.session_state.editing_thread_id = None
                    st.session_state.chat_threads = get_all_chats()

                    st.rerun()

            with col2:

                if st.button(
                    "❌ Cancel",
                    key=f"cancel_{thread_id}",
                    use_container_width=True
                ):

                    st.session_state.editing_thread_id = None

                    st.rerun()

        # ---------------- NORMAL MODE ----------------

        else:

            col1, col2, col3 = st.columns([6, 1, 1])

            with col1:

                if st.button(
                    f"💬 {title}",
                    key=f"chat_{thread_id}",
                    use_container_width=True
                ):

                    switch_chat(thread_id)

                    st.rerun()

            # Edit button
            with col2:

                if st.button(
                    "✏️",
                    key=f"edit_{thread_id}",
                    use_container_width=True
                ):

                    st.session_state.editing_thread_id = thread_id

                    st.rerun()

            # Archive button
            with col3:

                if st.button(
                    "🗑️",
                    key=f"archive_{thread_id}",
                    use_container_width=True
                ):

                    archive_chat(thread_id)

                    st.session_state.chat_threads = get_all_chats()

                    # If current chat was archived,
                    # switch to another available chat.
                    if thread_id == st.session_state.current_thread_id:

                        if st.session_state.chat_threads:

                            st.session_state.current_thread_id = (
                                st.session_state.chat_threads[0]["id"]
                            )

                        else:

                            new_thread_id = create_thread()

                            st.session_state.chat_threads = get_all_chats()

                            st.session_state.current_thread_id = (
                                new_thread_id
                            )

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


# ---------------- DISPLAY OLD MESSAGES ----------------

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

    # Set title from first user message
    if current_chat["title"] == "New Chat":

        new_title = user_input[:30]

        if len(user_input) > 30:

            new_title += "..."

        update_chat(
            current_thread_id,
            title=new_title
        )

    # Display user's message immediately
    with st.chat_message("user"):

        st.markdown(user_input)

    # Stream AI response
    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        full_response = ""

        for chunk in stream_chatbot(
            user_input,
            current_thread_id
        ):

            if chunk.content:

                full_response += chunk.content

                response_placeholder.markdown(
                    full_response
                )

    # Refresh chat metadata after response
    st.session_state.chat_threads = get_all_chats()

    st.rerun()
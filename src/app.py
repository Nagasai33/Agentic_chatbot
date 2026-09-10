import streamlit as st
from datetime import datetime, timedelta
MAX_MESSAGE_LENGTH = 10_000

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


# ---------------- SESSI
# ON STATE ----------------

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

def get_date_group(date_string):

    chat_date = datetime.fromisoformat(date_string).date()

    today = datetime.now().date()

    if chat_date == today:
        return "Today"

    elif chat_date == today.fromordinal(today.toordinal() - 1):
        return "Yesterday"

    else:
        return chat_date.strftime("%d %b %Y")


# ---------------- SIDEBAR ----------------

with st.sidebar:

    # ---------------- NEW CHAT ----------------

    if st.button(
        "＋ New chat",
        use_container_width=True
    ):

        create_new_chat()

        st.rerun()


    st.divider()


    # ---------------- CONVERSATIONS ----------------

    st.caption("Recent")

    # Always get latest chat metadata from database
    st.session_state.chat_threads = get_all_chats()


    current_group = None


    for chat in st.session_state.chat_threads:

        thread_id = chat["id"]
        title = chat["title"]
        updated_at = chat["updated_at"]


        # ---------------- DATE GROUP ----------------

        date_group = get_date_group(updated_at)


        if date_group != current_group:

            st.caption(date_group)

            current_group = date_group


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
                    use_container_width=True,
                    help="Save chat title"
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
                    "Cancel",
                    key=f"cancel_{thread_id}",
                    use_container_width=True,
                    help="Cancel renaming"
                ):

                    st.session_state.editing_thread_id = None

                    st.rerun()


        # ---------------- NORMAL MODE ----------------

        else:

            col1, col2, col3 = st.columns(
                [6, 1, 1]
            )


            # ---------------- CHAT BUTTON ----------------

            with col1:

                if (
                    thread_id
                    == st.session_state.current_thread_id
                ):

                    chat_label = f"● {title}"

                else:

                    chat_label = f"💬 {title}"


                if st.button(
                    chat_label,
                    key=f"chat_{thread_id}",
                    use_container_width=True
                ):

                    switch_chat(thread_id)

                    st.rerun()


            # ---------------- RENAME BUTTON ----------------

            with col2:

                if st.button(
                    "✏️",
                    key=f"edit_{thread_id}",
                    use_container_width=True,
                    help="Rename chat"
                ):

                    st.session_state.editing_thread_id = (
                        thread_id
                    )

                    st.rerun()


            # ---------------- ARCHIVE BUTTON ----------------

            with col3:

                if st.button(
                    "🗑️",
                    key=f"archive_{thread_id}",
                    use_container_width=True,
                    help="Archive chat"
                ):

                    archive_chat(thread_id)

                    st.session_state.chat_threads = (
                        get_all_chats()
                    )


                    # If current chat was archived,
                    # switch to another available chat.

                    if (
                        thread_id
                        == st.session_state.current_thread_id
                    ):

                        if st.session_state.chat_threads:

                            st.session_state.current_thread_id = (
                                st.session_state.chat_threads[0]["id"]
                            )

                        else:

                            new_thread_id = create_thread()

                            st.session_state.chat_threads = (
                                get_all_chats()
                            )

                            st.session_state.current_thread_id = (
                                new_thread_id
                            )


                    st.rerun()


    # ------------------------------------------------
    # IMPORTANT:
    # The following section is OUTSIDE the for-loop.
    # ------------------------------------------------

    st.divider()

    st.write("⚙️ Settings")

    st.write("👤 Profile")


# ---------------- MAIN CHAT ----------------

current_thread_id = st.session_state.current_thread_id

messages = get_current_messages()


# ---------------- EMPTY STATE ----------------

if not messages:

    # Add some vertical space
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    # Create three columns so the content
    # appears in the center of the main chat area.
    left_space, center_content, right_space = st.columns(
        [1, 2, 1]
    )

    with center_content:

        st.markdown(
            "<div style='text-align: center;'>"
            "<div style='font-size: 3rem;'>🤖</div>"
            "<h1>Agentic Chatbot</h1>"
            "<h3>How can I help you today?</h3>"
            "<p>Ask me anything and I'll help you "
            "solve, learn, or explore.</p>"
            "</div>",
            unsafe_allow_html=True
        )


# ---------------- DISPLAY OLD MESSAGES ----------------

else:

    for message in messages:

        if message.type == "human":

            role = "user"
            avatar = ":material/person:"

        elif message.type == "ai":

            role = "assistant"
            avatar = ":material/smart_toy:"

        else:

            continue


        with st.chat_message(
            role,
            avatar=avatar
        ):

            st.markdown(
                message.content
            )
            

# ---------------- CHAT INPUT ----------------

user_input = st.chat_input(
    "Ask me anything..."
)

if user_input and len(user_input) > MAX_MESSAGE_LENGTH:
    st.error(
        f"Your message is too long. "
        f"Please keep it under {MAX_MESSAGE_LENGTH:,} characters."
    )
    st.stop()

if user_input:
    user_input = user_input.strip()

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
    with st.chat_message("assistant", avatar=":material/smart_toy:"):

        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Thinking...")

        message_placeholder = st.empty()

        full_response = ""
        first_chunk = True

        try:

            for event in stream_chatbot(user_input, current_thread_id):

                if event["type"] == "tool":
                    thinking_placeholder.markdown("🔧 Using calculator...")

                elif event["type"] == "message":
                    if first_chunk:
                        thinking_placeholder.empty()
                        first_chunk = False

                    full_response += event["content"]
                    message_placeholder.markdown(full_response + "▌")
                elif event["type"] == "error":
                    thinking_placeholder.empty()
                    message_placeholder.error(event["content"]) 
                    break  

            message_placeholder.markdown(full_response)

        except Exception as e:

            thinking_placeholder.empty()
            message_placeholder.error(
                "Sorry, I couldn't generate a response right now. "
                "Please try again."
            )

            print(f"Chatbot error: {e}")

    # Refresh chat metadata after response
    st.session_state.chat_threads = get_all_chats()
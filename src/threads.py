import uuid
import sqlite3
from datetime import datetime

from graph import chatbot_graph, checkpointer


DB_PATH = "chatbot.db"


# ---------------- APPLICATION DATABASE ----------------

def init_database():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            thread_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            archived INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# Initialize application database
init_database()


# ---------------- CREATE THREAD ----------------

def create_thread():

    thread_id = str(uuid.uuid4())

    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT INTO chats (
            thread_id,
            title,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            thread_id,
            "New Chat",
            now,
            now
        )
    )

    conn.commit()
    conn.close()

    return thread_id


# ---------------- GET ALL THREADS ----------------

def get_all_threads():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute(
        """
        SELECT thread_id
        FROM chats
        WHERE archived = 0
        ORDER BY updated_at DESC
        """
    )

    threads = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return threads

#----------------get_all_threads----------------

def get_all_chats():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute(
        """
        SELECT
            thread_id,
            title,
            created_at,
            updated_at,
            archived
        FROM chats
        WHERE archived = 0
        ORDER BY updated_at DESC
        """
    )

    chats = []

    for row in cursor.fetchall():

        chats.append(
            {
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "archived": row[4]
            }
        )

    conn.close()

    return chats


# ---------------- UPDATE CHAT ----------------

def update_chat(
    thread_id,
    title=None
):

    conn = sqlite3.connect(DB_PATH)

    if title is not None:

        conn.execute(
            """
            UPDATE chats
            SET title = ?,
                updated_at = ?
            WHERE thread_id = ?
            """,
            (
                title,
                datetime.now().isoformat(),
                thread_id
            )
        )

    conn.commit()
    conn.close()

# ---------------- UPDATE CHAT ----------------

def archive_chat(thread_id):

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        UPDATE chats
        SET archived = 1,
            updated_at = ?
        WHERE thread_id = ?
        """,
        (
            datetime.now().isoformat(),
            thread_id
        )
    )

    conn.commit()
    conn.close()

# ---------------- NORMAL CHAT ----------------

def chatbot(message, thread_id):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    response = chatbot_graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        },
        config=config
    )

    return response["messages"][-1].content


# ---------------- STREAMING CHAT ----------------

def stream_chatbot(message, thread_id):
    config = {"configurable": {"thread_id": thread_id}}

    for mode, data in chatbot_graph.stream(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        stream_mode=["messages", "updates"]
    ):
        if mode == "messages":
            message_chunk, metadata = data

            if message_chunk.content:
                yield {
                    "type": "message",
                    "content": message_chunk.content
                }

        elif mode == "updates":
            if "tools" in data:
                yield {
                    "type": "tool",
                    "name": "calculator"
                }

    update_chat(thread_id)

# ---------------- GET THREAD MESSAGES ----------------

def get_thread_messages(thread_id):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    state = chatbot_graph.get_state(config)

    if state.values:

        return state.values.get(
            "messages",
            []
        )

    return []


# TEMPORARY TEST FUNCTION
def test_graph_updates(message, thread_id):
    config = {"configurable": {"thread_id": thread_id}}

    for update in chatbot_graph.stream(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        stream_mode="updates"
    ):
        print("UPDATE:", update)

def test_multi_stream(message, thread_id):
    config = {"configurable": {"thread_id": thread_id}}

    for event in chatbot_graph.stream(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        stream_mode=["messages", "updates"]
    ):
        print("EVENT:", event)
# ---------------- GET CHAT METADATA ----------------

def get_chat(thread_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute(
        """
        SELECT
            thread_id,
            title,
            created_at,
            updated_at,
            archived
        FROM chats
        WHERE thread_id = ?
        """,
        (thread_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "thread_id": row[0],
        "title": row[1],
        "created_at": row[2],
        "updated_at": row[3],
        "archived": row[4]
    }

   
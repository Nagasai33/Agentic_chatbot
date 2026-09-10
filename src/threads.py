import uuid
import sqlite3
from datetime import datetime, timedelta

from graph import chatbot_graph, checkpointer
INPUT_COST_PER_1M = 0.00
OUTPUT_COST_PER_1M = 0.00
MAX_THREAD_TOKENS = 10000
MAX_REQUESTS = 2
RATE_LIMIT_WINDOW_SECONDS = 60

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
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    
#------------save_token_usage()--------------------

def save_token_usage(
    thread_id,
    input_tokens,
    output_tokens,
    total_tokens
):
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT INTO token_usage (
            thread_id,
            input_tokens,
            output_tokens,
            total_tokens,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            thread_id,
            input_tokens,
            output_tokens,
            total_tokens,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()
    
#--------get_token_usage--------------

def get_token_usage(thread_id):
    conn = sqlite3.connect(DB_PATH)

    row = conn.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(input_tokens), 0),
            COALESCE(SUM(output_tokens), 0),
            COALESCE(SUM(total_tokens), 0)
        FROM token_usage
        WHERE thread_id = ?
        """,
        (thread_id,)
    ).fetchone()

    conn.close()

    cost = calculate_token_cost(
    input_tokens=row[1],
    output_tokens=row[2]
)

    return {
        "llm_calls": row[0],
        "input_tokens": row[1],
        "output_tokens": row[2],
        "total_tokens": row[3],
        "estimated_cost": cost,
    }
    
#---------budget-check function---------

def has_exceeded_token_budget(thread_id):
    usage = get_token_usage(thread_id)

    return usage["total_tokens"] >= MAX_THREAD_TOKENS

#----rate-limit function----------

def check_rate_limit(thread_id):
    conn = sqlite3.connect(DB_PATH)

    cutoff = (
        datetime.now()
        - timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)
    ).isoformat()

    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM request_log
        WHERE thread_id = ?
        AND created_at >= ?
        """,
        (thread_id, cutoff)
    ).fetchone()

    request_count = row[0]

    if request_count >= MAX_REQUESTS:
        conn.close()
        return False

    conn.execute(
        """
        INSERT INTO request_log (
            thread_id,
            created_at
        )
        VALUES (?, ?)
        """,
        (
            thread_id,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

    return True

#--------------cost calculation------------

def calculate_token_cost(input_tokens, output_tokens):
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_1M
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_1M

    return input_cost + output_cost

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

    if has_exceeded_token_budget(thread_id):
        yield {
            "type": "error",
            "content": "This conversation has reached its token limit."
        }
        return

    if not check_rate_limit(thread_id):
        yield {
            "type": "error",
            "content": "Too many requests. Please wait a moment and try again."
        }
        return

    config = {"configurable": {"thread_id": thread_id}}

    for mode, data in chatbot_graph.stream(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        stream_mode=["messages", "updates"]
    ):
        if mode == "messages":
            message_chunk, metadata = data

            usage = getattr(message_chunk, "usage_metadata", None)

            if usage:
                print("TOKEN USAGE:", usage)
                
                save_token_usage(
                    thread_id=thread_id,
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0)
                )
                

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

   
import uuid

from graph import chatbot_graph


# ---------------- CREATE THREAD ----------------

def create_thread():

    return str(uuid.uuid4())


# ---------------- CHAT WITH THREAD ----------------

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
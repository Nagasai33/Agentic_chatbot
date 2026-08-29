# 🤖 Agentic Chatbot

An AI-powered conversational chatbot built using **LangGraph, LangChain, Groq, and Streamlit**.

The project demonstrates how to build a modular conversational AI application using LangGraph for workflow orchestration, Groq for fast LLM inference, and Streamlit for the user interface.

## 🚀 Features

- 💬 ChatGPT-style conversational interface
- 🧵 Thread-based conversation management
- 🔄 Create and switch between multiple conversations
- 🧠 Conversation state management using LangGraph
- ⚡ Fast LLM inference using Groq
- 🖥️ Interactive Streamlit web interface
- 🔐 Environment-based API key management
- 🧩 Modular project architecture
- 📦 Dependency management using `requirements.txt`

## 🏗️ Architecture

The application follows a modular architecture where each component has a specific responsibility.

```text
                    Streamlit UI
                       app.py
                         │
                         ↓
                     threads.py
                         │
                         ↓
                      graph.py
                         │
                         ↓
                    LangGraph
                         │
                         ↓
                     nodes.py
                         │
                         ↓
                       llm.py
                         │
                         ↓
                    Groq API

📁 Project Structure
Agentic_chatbot/
│
├── src/
│   ├── __init__.py
│   ├── app.py              # Streamlit application
│   ├── graph.py            # LangGraph workflow and checkpointer
│   ├── llm.py              # Groq LLM configuration
│   ├── nodes.py             # LangGraph node functions
│   ├── state.py             # LangGraph state definition
│   └── threads.py           # Thread and conversation management
│
├── tests/                   # Test files
│
├── .env                    # API keys (not committed)
├── .gitignore
├── README.md
├── requirements.txt
└── venv/                   # Python virtual environment (not committed)

🛠️ Technologies Used
Python
LangGraph – workflow and state management
LangChain – LLM integration
Groq – LLM inference
Streamlit – web-based chat interface
Python-dotenv – environment variable management
Git & GitHub – version control
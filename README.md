# 🤖 Agentic AI Chatbot

A modular, persistent, and tool-enabled conversational AI application built with **Python, LangGraph, LangChain, Groq, SQLite, and Streamlit**.

This project is being developed incrementally to demonstrate how a simple LLM chatbot can evolve into a more capable **Agentic AI system** with persistent conversations, tool calling, streaming responses, file understanding, RAG, web search, and multimodal capabilities.

---

## 🚀 Project Overview

The goal of this project is to build an AI assistant that can:

- Maintain multiple conversations
- Persist conversations across application restarts
- Resume previous conversations
- Stream LLM responses in real time
- Execute external tools when required
- Display tool activity in the UI
- Process uploaded documents
- Perform document-based question answering using RAG
- Search the web
- Work with multiple tools
- Support image understanding
- Evolve toward a production-oriented Agentic AI architecture

The project is intentionally developed **one capability at a time**, with each feature implemented, tested, and integrated before moving to the next stage.

---

# ✨ Current Features

### 💬 Conversational AI

- ChatGPT-style conversational interface
- Multiple independent conversations
- Unique `thread_id` for every conversation
- Conversation history
- Resume previous conversations
- Conversation context maintained by LangGraph

### ⚡ Real-Time Streaming

- Real LLM response streaming
- Progressive token display
- "Thinking" state while generating
- Improved perceived response latency
- Streaming works with persistent conversations

### 🧵 Conversation Management

- Create new conversations
- Switch between conversations
- Automatically generated conversation titles
- Rename conversations
- Archive conversations
- Active/archived conversation management

### 💾 Persistent Storage

- SQLite-based persistence
- LangGraph checkpoint persistence
- Application-level chat metadata
- Conversations survive application restarts
- Separation between application metadata and LangGraph state

### 🛠️ Agentic Tool Calling

The chatbot can allow the LLM to decide when a tool is required.

Current implemented tool:

- 🧮 Calculator

The calculator supports basic arithmetic operations:

```text
+
-
*
/

🧠 Agentic Architecture

                         ┌─────────────────┐
                         │    Streamlit    │
                         │     app.py      │
                         └────────┬────────┘
                                  │
                                  ↓
                         ┌─────────────────┐
                         │   threads.py    │
                         │ Conversations   │
                         │ + DB operations │
                         └────────┬────────┘
                                  │
                                  ↓
                         ┌─────────────────┐
                         │    LangGraph    │
                         │    graph.py     │
                         └────────┬────────┘
                                  │
                         ┌────────┴────────┐
                         ↓                 ↓
                  ┌──────────────┐  ┌──────────────┐
                  │  chat_node   │  │   ToolNode   │
                  └──────┬───────┘  └──────┬───────┘
                         │                 │
                         ↓                 ↓
                  ┌──────────────┐  ┌──────────────┐
                  │  Groq LLM    │  │  Calculator  │
                  └──────┬───────┘  └──────┬───────┘
                         │                 │
                         └────────┬────────┘
                                  ↓
                           Final Response

🔄 Current Agent Workflow

User
 ↓
Streamlit
 ↓
threads.py
 ↓
LangGraph
 ↓
chat_node
 ↓
LLM
 ↓
Final response
For a tool-enabled question:

User
 ↓
Streamlit
 ↓
threads.py
 ↓
LangGraph
 ↓
chat_node
 ↓
LLM decides tool is required
 ↓
ToolNode
 ↓
Calculator
 ↓
ToolMessage
 ↓
chat_node
 ↓
LLM generates final answer
 ↓
Streamlit streams response

Example:
User:
Calculate 25 * 45

        ↓

LLM requests calculator

        ↓

Calculator:
25 * 45

        ↓

Tool result:
1125

        ↓

LLM:
The result is 1125.

🏗️ Project Structure

Agentic_chatbot/
│
├── src/
│   ├── __init__.py
│   │
│   ├── app.py
│   │   # Streamlit UI
│   │
│   ├── graph.py
│   │   # LangGraph workflow
│   │   # ToolNode
│   │   # Conditional routing
│   │   # SQLite checkpointer
│   │
│   ├── llm.py
│   │   # LLM configuration
│   │
│   ├── nodes.py
│   │   # LangGraph nodes
│   │   # Tool binding
│   │
│   ├── state.py
│   │   # LangGraph state definition
│   │
│   ├── threads.py
│   │   # Conversation management
│   │   # Application database operations
│   │   # Streaming interface
│   │
│   └── tools/
│       ├── __init__.py
│       └── calculator.py
│           # Safe arithmetic calculator tool
│
├── tests/
│   # Test files
│
├── .env
│   # API keys - NOT committed
│
├── .gitignore
│
├── chatbot.db
│   # Local SQLite database - NOT committed
│
├── requirements.txt
│
└── README.md

🧩 Core Components
 app.py

Responsible for the Streamlit user interface.

Responsibilities include:

Chat interface
Sidebar
New conversation creation
Conversation switching
Message rendering
Streaming responses
Tool activity display
Conversation rename
Conversation archive
UI state management

 threads.py

Responsible for conversation and application-level database operations.

Responsibilities include:

Creating conversations
Generating thread_id
Loading conversations
Updating conversation metadata
Renaming conversations
Archiving conversations
Retrieving conversation state
Streaming chatbot responses

This module acts as a bridge between the Streamlit UI and LangGraph.


graph.py

Responsible for constructing the LangGraph workflow.

Responsibilities include:

Creating the StateGraph
Adding graph nodes
Adding workflow edges
Conditional tool routing
Adding ToolNode
Configuring SQLite persistence
Compiling the graph

Current workflow:

START
  ↓
chat_node
  ↓
tools_condition
  ↓
 ┌───────────────┐
 │               │
 ↓               ↓
tools           END
 │
 ↓
chat_node
 │
 ↓
END
nodes.py

Contains the LangGraph node functions.

The chatbot node:

Receives conversation state
Sends messages to the LLM
Allows the LLM to request available tools
Returns the generated AI message

The LLM is connected to tools using LangChain's tool-binding mechanism.

state.py

Defines the LangGraph conversation state.

Current state:

class ChatState(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]

The message history can contain different message types such as:

HumanMessage
AIMessage
ToolMessage

This allows the graph to preserve the complete tool-calling interaction.

llm.py

Contains the LLM configuration.

The application currently uses:

Groq
  ↓
OpenAI-compatible API
  ↓
LangChain ChatOpenAI

The API key is loaded from environment variables rather than being hard-coded.

🛠️ Tool Architecture

The project uses LangChain tools together with LangGraph's ToolNode.

The architecture is:

LLM
 ↓
Tool Call
 ↓
LangGraph
 ↓
ToolNode
 ↓
Tool
 ↓
Tool Result
 ↓
LLM

The LLM does not directly execute Python functions.

Instead:

The LLM requests a tool.
LangGraph detects the tool call.
ToolNode executes the requested tool.
The result is added as a ToolMessage.
The LLM receives the tool result.
The LLM generates the final response.
🧮 Calculator Tool

The calculator is implemented as a LangChain tool.

It supports:

Addition
Subtraction
Multiplication
Division

Example:

Input:
25 * 45

Output:
1125

The calculator does not use Python's unrestricted eval().

Instead, the expression is parsed using Python's AST module and only explicitly allowed arithmetic operations are evaluated.

This reduces the risk of arbitrary Python code execution.

🧵 Thread-Based Conversations

Every conversation receives a unique thread_id.

Example:

thread_A → Conversation A
thread_B → Conversation B
thread_C → Conversation C

The thread ID allows LangGraph to keep different conversations isolated.

Conceptually:

Conversation A
     ↓
thread_id = A
     ↓
State A


Conversation B
     ↓
thread_id = B
     ↓
State B

Messages from one conversation are not automatically mixed with another conversation.

💾 Persistence Architecture

The application uses SQLite for persistent storage.

There are two conceptually different types of data:

                         chatbot.db
                             │
                 ┌───────────┴───────────┐
                 ↓                       ↓
       Application Database      LangGraph Checkpointer
                 │                       │
                 ↓                       ↓
          Chat Metadata          Conversation State
Application Database

Stores application-level information such as:

thread_id
title
created_at
updated_at
archived
LangGraph Checkpointer

Stores the graph's persistent conversation state and checkpoints.

This separation avoids unnecessarily duplicating the entire message history in the application metadata table.

🗃️ Application Database Schema

The application maintains a chats table.

Conceptually:

chats
├── thread_id
├── title
├── created_at
├── updated_at
└── archived
thread_id

Unique identifier for a conversation.

title

Conversation title displayed in the Streamlit sidebar.

created_at

Time when the conversation was created.

updated_at

Time when the conversation was last updated.

archived

Indicates whether the conversation is active or archived.

0 → Active
1 → Archived
🔁 Conversation Persistence

Example:

User:
"My name is Sai."

        ↓

Conversation state saved

        ↓

Application closes

        ↓

Application restarts

        ↓

User opens previous conversation

        ↓

Previous state is loaded

        ↓

User:
"What is my name?"

        ↓

AI:
"Your name is Sai."

This is achieved using:

LangGraph
    ↓
SqliteSaver
    ↓
SQLite
⚡ Real-Time Streaming

The chatbot supports real-time response streaming.

Instead of:

User
 ↓
LLM
 ↓
Wait
 ↓
Complete response
 ↓
Display

the application receives chunks progressively:

User
 ↓
LLM
 ↓
Chunk 1
 ↓
Chunk 2
 ↓
Chunk 3
 ↓
Chunk 4
 ↓
Streamlit

This makes the application feel more responsive.

For tool-enabled conversations, the application combines:

Message streaming
        +
Graph update events

This allows the UI to display tool activity while preserving real-time response streaming.

Example:

🔧 Using calculator...

The result of 25 × 45 is 1125.
🧠 Session State vs Persistent State

The application uses Streamlit session state for temporary UI information.

Examples:

Current selected conversation
Currently edited conversation
Temporary UI state

Persistent application data is stored in SQLite.

Therefore:

st.session_state
        ↓
Temporary UI state


SQLite
        ↓
Persistent application data
🔐 Environment Variables

API keys are stored in a .env file.

Example:

GROQ_API_KEY=your_groq_api_key

The application loads the key through environment variables.

Security

Never:

Hard-code API keys
Commit .env
Publish API keys
Put secrets inside source code

The .env file is excluded through .gitignore.

🛠️ Tech Stack
Technology	Purpose
Python	Core programming language
LangGraph	Agent/workflow orchestration
LangChain	LLM and tool integration
Groq	LLM inference
Streamlit	Web UI
SQLite	Persistent storage
LangGraph SQLite Checkpointer	Conversation persistence
python-dotenv	Environment variable management
Git	Version control
GitHub	Source code hosting
📦 Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>

Navigate into the project:

cd Agentic_chatbot
2. Create a virtual environment
python -m venv venv

Activate it on Windows PowerShell:

.\venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
🔑 Configure Environment Variables

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key

Do not commit this file to GitHub.

▶️ Run the Application

From the project root:

streamlit run src/app.py

The application will open in your browser.

🧪 Testing

The project is tested incrementally as new capabilities are added.

Current tested functionality includes:

Conversation Management
Create new conversation ✅
Switch conversations ✅
Multiple conversation isolation ✅
Rename conversation ✅
Archive conversation ✅
Persistence
Save conversation state ✅
Restart application ✅
Recover previous conversations ✅
Resume existing conversation ✅
Streaming
Real LLM streaming ✅
Progressive token display ✅
Streaming with persistent conversations ✅
Tool Calling
Calculator tool invocation ✅
Tool execution through ToolNode ✅
Tool result returned to LLM ✅
Final response after tool execution ✅
Tool activity displayed in UI ✅
Normal questions bypass calculator ✅
Calculator Security
Basic arithmetic supported ✅
Restricted AST evaluation ✅
No unrestricted eval() execution ✅
🗺️ Development Roadmap

The project is being developed incrementally.

Step 1 — Simple LangGraph Chatbot

Status: ✅ Completed

Implemented:

LangGraph workflow
Chat state
Chat node
Groq LLM integration
Basic conversational flow

Architecture:

START
 ↓
chat_node
 ↓
END
Step 2 — Persistent Chat

Status: ✅ Completed

Implemented:

Unique conversation threads
thread_id
SQLite persistence
LangGraph SqliteSaver
Persistent conversation state
Conversation recovery after restart
Step 3 — Streaming Responses

Status: ✅ Completed

Implemented:

LangGraph streaming
Progressive response rendering
Real LLM streaming
Streaming with persistent conversations
Step 4 — Resume Conversations

Status: ✅ Completed

Implemented:

Previous conversation retrieval
Sidebar conversation selection
Existing thread_id reuse
Previous message loading
Conversation continuation
Multiple conversation isolation
Step 5 — Database Integration

Status: ✅ Completed

Implemented:

Application-level SQLite database
chats table
Chat metadata management
Create chat
Read chat
Update chat
Rename chat
Archive chat
Persistent titles
Separation between application data and LangGraph state
Step 6 — Advanced Chat UI

Status: ✅ Completed

Implemented:

ChatGPT-style interface
Improved sidebar
Conversation controls
Message rendering
Streaming UX
Thinking/loading state
Rename functionality
Archive functionality
Active conversation indication
Improved conversation organization
Step 7 — Agentic Tools, Files, RAG & Search

Status: 🚧 In Progress

Phase A — Tool Calling Fundamentals

Status: ✅ Completed

Learned and implemented:

Tools
Tool calling
bind_tools()
ToolNode
Conditional tool routing
AIMessage
ToolMessage
Agent vs LLM concepts
Phase B — Calculator Tool

Status: ✅ Completed

Implemented:

Calculator tool
Safe arithmetic evaluation
AST-based expression parsing
Tool validation
Calculator testing
Phase C — LangGraph Agent/Tool Loop

Status: ✅ Completed

Implemented:

chat_node
    ↓
tools_condition
    ↓
ToolNode
    ↓
calculator
    ↓
chat_node
Phase D — Tool Activity in UI

Status: ✅ Completed

Implemented:

Tool execution detection
Graph update streaming
Real token streaming
Tool activity display
Calculator activity indicator
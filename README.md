# 🤖 Agentic AI Chatbot

A production-oriented conversational AI chatbot built with **Python, LangGraph, LangChain, Groq, Tavily, SQLite, and Streamlit**.

The application combines an LLM with external tools so that the chatbot can decide when to answer directly, perform calculations, or search the web for current information.

---

## 🚀 Features

- 💬 ChatGPT-style conversational interface
- 🧵 Multiple independent conversations
- 🆔 Unique `thread_id` for each conversation
- 💾 Persistent conversations using SQLite
- 🔄 Resume previous conversations after application restart
- ⚡ Real-time LLM response streaming
- 📝 Automatic conversation titles
- ✏️ Rename conversations
- 📦 Archive conversations
- 🧠 LangGraph-based agent workflow
- 🧮 Safe calculator tool
- 🔎 Tavily web-search tool
- 🔀 Automatic tool selection by the LLM
- 🔧 Tool activity indicators in the UI
- 🛡️ Calculator input and complexity protection
- 📏 Conversation history/token-budget control
- 🔐 Environment-variable based API-key management
- 📦 Dependency management with `requirements.txt`

---

# 🏗️ Architecture

The chatbot follows an agentic tool-calling architecture.

```text
                         User
                          │
                          ▼
                    Streamlit UI
                       app.py
                          │
                          ▼
                     threads.py
                          │
                          ▼
                     LangGraph
                       graph.py
                          │
                          ▼
                      chat_node
                       nodes.py
                          │
                          ▼
                       Groq LLM
                    gpt-oss-20b
                          │
                ┌─────────┴─────────┐
                │                   │
          Direct Answer        Tool Required
                                    │
                              ┌─────┴─────┐
                              │           │
                              ▼           ▼
                         Calculator    Tavily
                              │        Web Search
                              └─────┬─────┘
                                    │
                                    ▼
                               Tool Result
                                    │
                                    ▼
                                  LLM
                                    │
                                    ▼
                              Final Response
```

---

# 🔄 Agent Workflow

For a normal question:

```text
User
 ↓
Streamlit
 ↓
LangGraph
 ↓
LLM
 ↓
Final Answer
```

For a calculation:

```text
User
 ↓
LLM
 ↓
Calculator Tool
 ↓
Tool Result
 ↓
LLM
 ↓
Final Answer
```

For a current-information question:

```text
User
 ↓
LLM
 ↓
Tavily Web Search
 ↓
Search Results
 ↓
LLM
 ↓
Final Answer
```

The LLM decides whether a tool is required.

---

# 🧠 LangGraph Workflow

The graph contains an agent node and a tool execution node.

```text
START
  │
  ▼
chat_node
  │
  ▼
tools_condition
  │
  ├───────────────► END
  │
  ▼
ToolNode
  │
  ▼
Tool
  │
  ▼
chat_node
  │
  ▼
END
```

The tool loop allows the LLM to:

1. Receive the user request.
2. Decide whether a tool is necessary.
3. Request the appropriate tool.
4. Execute the tool through LangGraph's `ToolNode`.
5. Receive the tool result.
6. Generate the final response.

---

# 🛠️ Tools

## 🧮 Calculator

The calculator supports:

- Addition
- Subtraction
- Multiplication
- Division

Example:

```text
User:
Calculate 25 * 45

Assistant:
25 × 45 = 1125
```

The calculator does **not** use unrestricted Python `eval()`.

Instead, the expression is parsed using Python's `ast` module and only explicitly allowed arithmetic operations are evaluated.

### Calculator safety controls

```text
MAX_EXPRESSION_LENGTH = 500
MAX_NUMBER_DIGITS = 100
MAX_AST_NODES = 100
```

The calculator also handles:

- Division by zero
- Invalid expressions
- Excessively large numbers
- Overly complex expressions
- Invalid input types

---

# 🔎 Tavily Web Search

The chatbot uses **Tavily** to retrieve current information from the web.

Example:

```text
User:
What are the latest developments in AI agents in 2026?
```

The agent can decide to use Tavily instead of relying only on the LLM's training knowledge.

The current configuration uses a limited number of search results to reduce unnecessary context usage.

```text
Tavily
  ↓
Search Web
  ↓
Return Relevant Results
  ↓
LLM
  ↓
Current Answer
```

Example UI behavior:

```text
🔎 Searching the web...
```

---

# 🧠 Conversation History Management

The application limits the amount of previous conversation history sent to the LLM.

This helps control:

- Context size
- API usage
- Response latency
- Token consumption

The current conversation-history configuration uses a token budget rather than sending unlimited history.

The project also limits Tavily search results to reduce excessive context consumption.

This is particularly important when using web search because search results can contain substantially more text than a normal conversation message.

---

# 💾 Persistent Conversations

The application uses SQLite for persistence.

There are two conceptual layers:

```text
                    chatbot.db
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
     Application Database    LangGraph Checkpointer
              │                   │
              ▼                   ▼
       Chat Metadata       Conversation State
```

### Application database

Stores information such as:

```text
thread_id
title
created_at
updated_at
archived
```

### LangGraph checkpointer

Stores the graph's persistent conversation state.

This allows users to close and restart the application without losing their conversations.

---

# 🧵 Thread-Based Conversations

Every conversation receives a unique `thread_id`.

```text
thread_A → Conversation A

thread_B → Conversation B

thread_C → Conversation C
```

This keeps conversations isolated.

For example:

```text
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
```

Messages from one conversation are not automatically mixed with another conversation.

---

# ⚡ Real-Time Streaming

The application streams LLM responses progressively.

Instead of:

```text
User
 ↓
LLM
 ↓
Wait
 ↓
Complete response
 ↓
Display
```

the application uses:

```text
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
```

This improves perceived response latency.

The UI also displays tool activity while tools are executing.

Examples:

```text
🔧 Using calculator...
```

and:

```text
🔎 Searching the web...
```

---

# 📁 Project Structure

```text
Agentic_chatbot/
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   │   └── Streamlit UI
│   │
│   ├── graph.py
│   │   └── LangGraph workflow
│   │
│   ├── llm.py
│   │   └── Groq LLM configuration
│   │
│   ├── nodes.py
│   │   └── Agent node and tool binding
│   │
│   ├── state.py
│   │   └── LangGraph state definition
│   │
│   ├── threads.py
│   │   └── Conversation and database operations
│   │
│   └── tools/
│       ├── __init__.py
│       ├── calculator.py
│       │   └── Safe calculator
│       │
│       └── web_search.py
│           └── Tavily web search
│
├── test/
│   └── test_tavily.py
│
├── .env
│   └── API keys - NOT committed
│
├── .gitignore
├── requirements.txt
├── README.md
└── chatbot.db
    └── Local database - NOT committed
```

---

# 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangGraph | Agent workflow orchestration |
| LangChain | LLM and tool integration |
| Groq | LLM inference |
| `gpt-oss-20b` | LLM used by the application |
| Tavily | Web search |
| Streamlit | Web interface |
| SQLite | Persistent storage |
| LangGraph SQLite Checkpointer | Conversation persistence |
| python-dotenv | Environment variable management |
| Git | Version control |
| GitHub | Source code hosting |

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Never hard-code API keys in the source code.

Never commit `.env` to GitHub.

The `.gitignore` file excludes:

```text
.env
chatbot.db
chatbot.db-shm
chatbot.db-wal
__pycache__/
*.pyc
venv/
```

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

## 2. Navigate into the project

```bash
cd Agentic_chatbot
```

## 3. Create a virtual environment

```bash
python -m venv venv
```

## 4. Activate the virtual environment

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

From the project root:

```bash
streamlit run src/app.py
```

The application will open in your browser.

---

# 🧪 Tested Functionality

The current implementation has been tested for:

### Conversation Management

- Create new conversation ✅
- Switch conversations ✅
- Multiple conversation isolation ✅
- Rename conversation ✅
- Archive conversation ✅

### Persistence

- SQLite persistence ✅
- Resume previous conversations ✅
- Conversation survives application restart ✅

### Streaming

- Real-time LLM streaming ✅
- Progressive response rendering ✅
- Tool activity indicators ✅

### Calculator

- Basic arithmetic ✅
- Safe AST evaluation ✅
- Division-by-zero handling ✅
- Large-number protection ✅
- Expression-length protection ✅
- AST-complexity protection ✅

### Tavily

- Tavily API connection ✅
- Web search execution ✅
- LLM tool routing to Tavily ✅
- Current-information questions ✅
- Tavily activity indicator ✅

### Token / Context Control

- Conversation history limiting ✅
- Tavily result limiting ✅
- Reduced context usage for web searches ✅
- Groq TPM protection through context control ✅

---

# 🧪 Example Queries

### Normal question

```text
What is an AI agent?
```

### Calculator

```text
Calculate 125 * 48
```

Expected:

```text
125 × 48 = 6000
```

### Web search

```text
What are the latest developments in AI agents in 2026?
```

### Current news

```text
What are the latest developments in Andhra Pradesh?
```

### Conversation memory

```text
My name is Sai.
```

Then:

```text
What is my name?
```

---

# 🛡️ Reliability and Safety

The project includes several production-oriented protections.

### Calculator

- Restricted arithmetic operations
- AST-based evaluation
- Maximum expression length
- Maximum number size
- Maximum AST complexity
- Division-by-zero handling

### Conversation

- Limited conversation history
- Token-budget control
- Separate conversation threads
- Persistent checkpoints

### API usage

- Controlled Tavily result count
- Request timeout
- Retry handling
- User-friendly error messages
- Context-size control

---

# ⚠️ Current Limitations

This project is designed as a portfolio and learning project rather than a fully production-hosted enterprise system.

Current limitations include:

- Tavily search results consume additional context.
- Groq API usage is subject to provider rate and token limits.
- SQLite is suitable for local/small-scale usage but is not ideal for high-concurrency production deployments.
- Web-search results depend on Tavily's search quality and availability.
- API keys are required for LLM and web-search functionality.

---

# 🎯 Project Goal

The goal of this project is to demonstrate the evolution of a traditional chatbot into an **Agentic AI application**.

The final architecture combines:

```text
LLM
 +
Memory
 +
Tools
 +
Web Search
 +
Persistent State
 +
Streaming
 +
Tool Routing
```

The system demonstrates how an LLM can move beyond simply generating text and instead:

```text
Understand Request
       ↓
Decide Action
       ↓
Select Tool
       ↓
Execute Tool
       ↓
Observe Result
       ↓
Generate Final Response
```

---

# 📌 Current Status

| Component | Status |
|---|---|
| LangGraph chatbot | ✅ Complete |
| Groq LLM integration | ✅ Complete |
| SQLite persistence | ✅ Complete |
| Conversation management | ✅ Complete |
| Streaming responses | ✅ Complete |
| Calculator tool | ✅ Complete |
| Tool routing | ✅ Complete |
| Tool activity UI | ✅ Complete |
| Tavily web search | ✅ Complete |
| Context/token control | ✅ Complete |
| Git/GitHub preparation | 🔄 Finalizing |
| Deployment | 🔄 Next |

---

# 👨‍💻 Development Philosophy

The project was developed incrementally.

Each major capability was:

```text
Learn
 ↓
Implement
 ↓
Test
 ↓
Debug
 ↓
Integrate
 ↓
Harden
```

This approach helped build the application while understanding the underlying Agentic AI concepts rather than simply assembling libraries.

---

# 📄 License

This project is intended for educational, portfolio, and demonstration purposes.
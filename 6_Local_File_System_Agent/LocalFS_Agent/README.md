# LocalFS Agent

**LocalFS Agent** is an AI-powered file system assistant that allows you to interact with your local files and folders using natural language. Built with LangChain, Groq, and Multi-Server MCP, it provides tools for searching, reading, writing, organizing, and analyzing files—all from an interactive chat interface.

---
## Features

- **File Search & Organization**
  - Search files by name, extension, or type
  - List files in specific folders
  - Identify duplicates and large/small files
  - Group files by extension and analyze top file types

- **Time & Size-Based Queries**
  - Recently modified files
  - Files modified today
  - Files larger/smaller than a specified size

- **File Manipulation**
  - Read, write, append, move, copy, rename files
  - Create and delete folders
  - Delete files safely

- **Interactive Chat**
  - LLM-powered chat interface to query, analyze, and organize your filesystem
  - Configurable roots, model, temperature, and API keys
  - Supports light/dark mode for user interface

---

## Demo Example

```text
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║🚀  Welcome to the LocalFS Agent Interactive Console  🚀 ║
║                                                          ║
║   Your smart file assistant is ready to help you:        ║
║     • Search files & folders                             ║
║     • Read, write, delete files                          ║
║     • Organize your directories                          ║
║                                                          ║
║   💡 Type 'exit' anytime to quit the loop                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

**Example interaction:**

```text
You: what root path you have
AI: The allowed root path is: 'C:\Users\manas\OneDrive\Desktop\Bright_data'

You: create a text file my_story with content "A young boy stood by the riverbank..."
AI: File created: C:\Users\manas\OneDrive\Desktop\Bright_data\my_story.txt

You: arrange files by size
AI: Files in ascending order:
    1. requirements.txt
    2. .env
    3. test.ipynb
    4. main.py
    5. my_story.txt

You: delete my_story.txt
AI: File deleted successfully.
```

---

## Architecture

- **Server**
  - `FileOps_helper.py` runs as an MCP server using `streamable-http`
  - Exposes file tools for the agent
  - Built with FastMCP

- **Client**
  - Connects to the MCP server
  - Loads available tools and creates a React-style agent (`create_react_agent`)
  - Processes natural language input and outputs file-related actions

- **Streamlit UI**
  - Interactive interface for chatting with the agent
  - Sidebar for configuration: roots, temperature, model, API keys
  - Light/Dark mode toggle
  - Async communication with the MCP server

---

## Requirements

- Python 3.12+
- MCP: `pip install mcp langchain-mcp-adapters langgraph`
- LangChain: `pip install langchain langchain-groq`
- Streamlit: `pip install streamlit`
- Other dependencies: `requests`, `python-dotenv`, `nest_asyncio`

---

## Installation 

1. Clone the repository:

```bash
git clone <repo_url>
cd LocalFS_Agent
```
2. Install dependencies:

```bash
pip install -r requirements.txt
```
3. Add your API keys to `.env`:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

---
4. Run the **server**:

```bash
python server/FileOps_helper.py
```

5. Run the **interactive client**:

```bash
python server/client.py
```

> **Note:** The agent is currently configured to work with the root folder:  
> `C:\Users\manas\OneDrive\Desktop\Bright_data`. Update `roots` in `client.py` to add more folders.

---
###  Run the Streamlit UI

```bash
streamlit run ui.py
```

Use the sidebar to configure roots, model, temperature, and API keys, and start chatting with the LocalFS Agent.

## Notes

- Ensure the MCP server is running before starting the client


## License

MIT License

---

## Author

**Manas Kumar**  
 AI Enthusiast





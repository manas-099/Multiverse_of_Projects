# 🚀 StackSnap – Snapshot Your Repo Stack in Seconds

StackSnap analyzes any GitHub repository and generates a clear breakdown of its tech stack in **point-wise format** using **LLMs**.

---

## 📸 Screenshot
Here’s how the UI looks:

![UI Screenshot](assets/screenshot.png)

---

## 📂 Project Structure

```
StackSnap/
│── src/
│   ├── stacksnap/
│   │   ├── agent/          # LangGraph workflow
│   │   ├── backend/        # FastAPI backend
│   │   ├── frontend/       # HTML, CSS, JS frontend
│   │   ├── prompt_library/ # Prompt templates
│   │   ├── tools/          # Repo stack analyzer
│   │   └── utils/          # Model loader, helpers
│── pyproject.toml
│── requirements.txt
│── README.md
```

---

## 🧠 LLM Used
- **Gemini ** – used for analyzing repository stack information.

🔑 API Key is required in `.env` file:
```

GOOGLE_API_KEY=""
```

---

## ⚙️ How It Works
1. User enters a **GitHub repo URL** in the frontend.
2. FastAPI backend receives the URL → runs `stacks_analyzer`.
3. Extracted stack info is passed to **Gemini LLM** using LangGraph workflow.
4. LLM formats and summarizes stack details in **point-wise bullet style**.
5. Frontend displays formatted results beautifully.

---

## 🛠 Tech Stack
- **Backend:** FastAPI, LangGraph, LangChain
- **Frontend:** HTML, CSS, JavaScript
- **LLM:** Gemini (Google Generative AI)
- **Utils:** python-dotenv for env vars
- **Other Libraries:** sentence-transformers, beautifulsoup4, streamlit

---

## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/manas-099/Multiverse_of_Projects/tree/main/7_stack-analyzer/StackSnap
cd stacksnap
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Or with Poetry (if using `pyproject.toml`):
```bash
poetry install
```

---

## ▶️ Running the Project

1. Start backend server:
```bash
uvicorn stacksnap.backend.main:app --reload --port 8000
```

2. Open frontend:
Simply open `src/stacksnap/frontend/index.html` in your browser.

---

## 📑 Requirements

Example `requirements.txt`:

```
fastapi
uvicorn
langchain
langgraph
langchain-core
python-dotenv


```

Example `pyproject.toml` (dependencies section):

```toml
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.110.0"
uvicorn = "^0.29.0"
langchain = "^0.2.0"
langgraph = "^0.1.0"
langchain-core = "^0.2.0"
python-dotenv = "^1.0.1"

```

---


---

## 👨‍💻 Author
Built by **Manas patra** 🚀

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from stacksnap.agent.workflow import analyze_repo
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="StackSnap API")


# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to ["http://127.0.0.1:5500"] if using Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body
class RepoRequest(BaseModel):
    repo_url: str

# Load LangGraph app once
graph_app = analyze_repo()
def format_result_text(text: str) -> str:
    """Convert \n text into HTML-friendly format with bullets."""

   
    formatted = (
        text.replace("\n\n", "<br><br>")   # Paragraph breaks
            .replace("\n-", "<br>•")       # Convert list items to bullets
            .replace("\n", "<br>")         # Single newlines
    )
    return formatted
@app.post("/analyze")
async def analyze_repo_endpoint(request: RepoRequest):
    try:

        response = graph_app.invoke({"repo_url": request.repo_url})
        if "result" in response:
            print(response["result"])
            response = format_result_text(response["result"])
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
